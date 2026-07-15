"""
ROM 数据核心调度类

作为 ROM 编辑器的数据中枢，管理所有已解析的 ROM 数据，
并提供对各个文件模块（ROBOT.RAF 等）的统一读写调度。
缓存路径从 config 模块自动获取。

Classes:
    Rom: ROM 数据核心调度类
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import config

from . import dc_bin, dr_bin, pilot_bin, robot_raf, sndata_bin, snmsg_bin
from .codec.extra import (
    DC_TEXT_EXTRA,
    DR_TEXT_EXTRA,
    PILOT_EXTRA,
    ROBOT_EXTRA,
    SNMSG_TEXT_EXTRA,
)


class Rom:
    """ROM 数据核心调度类 - 存储已加载的 ROM 数据并提供文件读写接口"""

    # 各文件在缓存目录下的相对路径（因游戏 ISO 结构固定而写死）
    _FILE_PATHS: dict[str, str] = {
        "robots": "UNITPRAM/ROBOT.RAF",
        "pilots": "UNITPRAM/PILOT.BIN",
        "snmsgs": "SNMAP/SNMSG.BIN",
        "sndata": "SNMAP/SNDATA.BIN",
        "dc": "OPTION/DC.BIN",
        "dr": "OPTION/DR.BIN",
    }

    # 文件 key → 对应的方法名（read_cache / write_cache 通过此表分发）
    _LOAD_DISPATCH: dict[str, str] = {
        "robots": "load_robots",
        "pilots": "load_pilots",
        "snmsgs": "load_snmsgs",
        "sndata": "load_sndata",
        "dc": "load_dc",
        "dr": "load_dr",
    }
    _SAVE_DISPATCH: dict[str, str] = {
        "robots": "save_robots",
        "pilots": "save_pilots",
        "snmsgs": "save_snmsgs",
        "sndata": "save_sndata",
        "dc": "save_dc",
        "dr": "save_dr",
    }

    def __init__(self):
        """初始化数据存储字典"""
        self._data: dict[str, dict] = {}

    # ========== 路径管理 ==========

    @property
    def cache_dir(self) -> str:
        """缓存目录路径（来自 config.option.cache_dir）"""
        return os.path.join(
            config.current_path,
            config.option.cache_dir.value,
        )

    @property
    def xml_path(self) -> str:
        """cache.xml 项目文件路径（由 cache_dir 推导）"""
        return os.path.join(
            os.path.dirname(self.cache_dir),
            os.path.basename(self.cache_dir) + ".xml",
        )

    # ========== 数据访问 ==========

    def __getitem__(self, key: str) -> dict:
        """按 key 获取已解析的数据"""
        return self._data[key]

    def __setitem__(self, key: str, value: dict):
        """设置指定 key 的解析数据"""
        self._data[key] = value

    def __contains__(self, key: str) -> bool:
        """判断指定 key 是否已加载"""
        return key in self._data

    def get(self, key: str, default=None):
        """获取已解析的数据，不存在时返回 default"""
        return self._data.get(key, default)

    def keys(self):
        """返回所有已加载的数据 key 视图"""
        return self._data.keys()

    def clear(self):
        """清空所有已解析的数据"""
        self._data.clear()

    # ========== 缓存批量读写（供 UI 槽函数调用） ==========

    def read_cache(self) -> None:
        """并行读取并解析缓存目录下所有已注册的数据文件

        通过 ThreadPoolExecutor 并行调度 _LOAD_DISPATCH 中各 load_* 方法，
        总耗时 ≈ 最慢的那个文件。各 load_* 在 C 扩展层释放 GIL，可安全并发。

        Raises:
            FileNotFoundError: 缓存目录不存在
            RuntimeError: 部分文件加载失败（汇总所有错误后抛出）
        """
        if not os.path.isdir(self.cache_dir):
            raise FileNotFoundError(f"Cache directory not found: {self.cache_dir}")

        errors: dict[str, Exception] = {}

        with ThreadPoolExecutor(max_workers=len(self._LOAD_DISPATCH)) as pool:
            future_to_key = {pool.submit(getattr(self, method)): key for key, method in self._LOAD_DISPATCH.items()}
            for future in as_completed(future_to_key):
                key = future_to_key[future]
                try:
                    future.result()
                except Exception as exc:
                    errors[key] = exc

        if errors:
            details = "; ".join(f"{k}: {v}" for k, v in errors.items())
            raise RuntimeError(f"Failed to load files: {details}")

        self.dump_to_txt()

    def write_cache(self) -> None:
        """将所有已修改的数据构建并写回缓存目录

        遍历 _data 中已存在的 key，通过 _SAVE_DISPATCH 分发到 save_* 方法。
        """
        for key in self._data:
            method_name = self._SAVE_DISPATCH.get(key)
            if method_name is None:
                continue
            getattr(self, method_name)()

    # ========== 单文件读写：DC.BIN ==========

    def load_dc(self, extra: dict | None = None) -> dict:
        """从缓存目录加载并解析 DC.BIN

        Args:
            extra: 文本映射字典（默认 DC_TEXT_EXTRA），传给 codec 解码

        Returns:
            解析后的角色图鉴数据 dict

        Raises:
            FileNotFoundError: 文件不存在
            RuntimeError: 解析/解压失败
        """
        if extra is None:
            extra = DC_TEXT_EXTRA
        path = os.path.join(self.cache_dir, self._FILE_PATHS["dc"])
        if not os.path.isfile(path):
            raise FileNotFoundError(f"DC.BIN not found: {path}")

        with open(path, "rb") as f:
            raw = f.read()

        data = dc_bin.parse(raw, extra=extra)
        self._data["dc"] = data
        return data

    def save_dc(self, extra: dict | None = None) -> None:
        """将角色图鉴数据构建并写回缓存目录下的 DC.BIN

        Args:
            extra: 文本映射字典（默认 DC_TEXT_EXTRA），传给 codec 编码

        Raises:
            KeyError: 尚未加载角色图鉴数据
            RuntimeError: 构建/压缩失败
        """
        if extra is None:
            extra = DC_TEXT_EXTRA
        data = self._data.get("dc")
        if data is None:
            raise KeyError("No DC data loaded. Call load_dc() first.")

        raw = dc_bin.build(data, extra=extra)

        path = os.path.join(self.cache_dir, self._FILE_PATHS["dc"])
        with open(path, "wb") as f:
            f.write(raw)

    # ========== 单文件读写：DR.BIN ==========

    def load_dr(self, extra: dict | None = None) -> dict:
        """从缓存目录加载并解析 DR.BIN

        Args:
            extra: 文本映射字典（默认 DR_TEXT_EXTRA），传给 codec 解码

        Returns:
            解析后的机体图鉴数据 dict

        Raises:
            FileNotFoundError: 文件不存在
            RuntimeError: 解析/解压失败
        """
        if extra is None:
            extra = DR_TEXT_EXTRA
        path = os.path.join(self.cache_dir, self._FILE_PATHS["dr"])
        if not os.path.isfile(path):
            raise FileNotFoundError("DR.BIN not found: " + path)

        with open(path, "rb") as f:
            raw = f.read()

        data = dr_bin.parse(raw, extra=extra)
        self._data["dr"] = data
        return data

    def save_dr(self, extra: dict | None = None) -> None:
        """将机体图鉴数据构建并写回缓存目录下的 DR.BIN

        Args:
            extra: 文本映射字典（默认 DR_TEXT_EXTRA），传给 codec 编码

        Raises:
            KeyError: 尚未加载机体图鉴数据
            RuntimeError: 构建/压缩失败
        """
        if extra is None:
            extra = DR_TEXT_EXTRA
        data = self._data.get("dr")
        if data is None:
            raise KeyError("No DR data loaded. Call load_dr() first.")

        raw = dr_bin.build(data, extra=extra)

        path = os.path.join(self.cache_dir, self._FILE_PATHS["dr"])
        with open(path, "wb") as f:
            f.write(raw)

    # ========== 单文件读写：PILOT.BIN ==========

    def load_pilots(self, extra: dict | None = None) -> dict:
        """从缓存目录加载并解析 PILOT.BIN

        Args:
            extra: 文本映射字典（默认 PILOT_EXTRA），传给 codec 解码

        Returns:
            解析后的驾驶员数据 dict

        Raises:
            FileNotFoundError: 文件不存在
            RuntimeError: 解析/解压失败
        """
        if extra is None:
            extra = PILOT_EXTRA
        path = os.path.join(self.cache_dir, self._FILE_PATHS["pilots"])
        if not os.path.isfile(path):
            raise FileNotFoundError(f"PILOT.BIN not found: {path}")

        with open(path, "rb") as f:
            raw = f.read()

        data = pilot_bin.parse(raw, extra=extra)
        self._data["pilots"] = data
        return data

    def save_pilots(self, extra: dict | None = None) -> None:
        """将驾驶员数据构建并写回缓存目录下的 PILOT.BIN

        Args:
            extra: 文本映射字典（默认 PILOT_EXTRA），传给 codec 编码

        Raises:
            KeyError: 尚未加载驾驶员数据
            RuntimeError: 构建/压缩失败
        """
        if extra is None:
            extra = PILOT_EXTRA
        data = self._data.get("pilots")
        if data is None:
            raise KeyError("No pilot data loaded. Call load_pilots() first.")

        raw = pilot_bin.build(data, extra=extra)

        path = os.path.join(self.cache_dir, self._FILE_PATHS["pilots"])
        with open(path, "wb") as f:
            f.write(raw)

    # ========== 单文件读写：ROBOT.RAF ==========

    def load_robots(self, extra: dict | None = None) -> dict:
        """从缓存目录加载并解析 ROBOT.RAF

        Args:
            extra: 文本映射字典（默认 ROBOT_EXTRA），传给 codec 解码

        Returns:
            解析后的机体数据 dict

        Raises:
            FileNotFoundError: 文件不存在
            RuntimeError: 解析/解压失败
        """
        if extra is None:
            extra = ROBOT_EXTRA
        path = os.path.join(self.cache_dir, self._FILE_PATHS["robots"])
        if not os.path.isfile(path):
            raise FileNotFoundError(f"ROBOT.RAF not found: {path}")

        with open(path, "rb") as f:
            raw = f.read()

        data = robot_raf.parse(raw, extra=extra)
        self._data["robots"] = data
        return data

    def save_robots(self, extra: dict | None = None) -> None:
        """将机体数据构建并写回缓存目录下的 ROBOT.RAF

        Args:
            extra: 文本映射字典（默认 ROBOT_EXTRA），传给 codec 编码

        Raises:
            KeyError: 尚未加载机体数据
            RuntimeError: 构建/压缩失败
        """
        if extra is None:
            extra = ROBOT_EXTRA
        data = self._data.get("robots")
        if data is None:
            raise KeyError("No robot data loaded. Call load_robots() first.")

        raw = robot_raf.build(data, extra=extra)

        path = os.path.join(self.cache_dir, self._FILE_PATHS["robots"])
        with open(path, "wb") as f:
            f.write(raw)

    # ========== 单文件读写：SNDATA.BIN ==========

    def load_sndata(self) -> dict:
        """从缓存目录加载并解析 SNDATA.BIN

        Returns:
            解析后的场景数据 dict

        Raises:
            FileNotFoundError: 文件不存在
        """
        path = os.path.join(self.cache_dir, self._FILE_PATHS["sndata"])
        if not os.path.isfile(path):
            raise FileNotFoundError(f"SNDATA.BIN not found: {path}")

        with open(path, "rb") as f:
            raw = f.read()

        data = sndata_bin.parse(raw)
        self._data["sndata"] = data
        return data

    def save_sndata(self) -> None:
        """将场景数据构建并写回缓存目录下的 SNDATA.BIN

        Raises:
            KeyError: 尚未加载场景数据
        """
        data = self._data.get("sndata")
        if data is None:
            raise KeyError("No SNDATA data loaded. Call load_sndata() first.")

        raw = sndata_bin.build(data)

        path = os.path.join(self.cache_dir, self._FILE_PATHS["sndata"])
        with open(path, "wb") as f:
            f.write(raw)

    # ========== 单文件读写：SNMSG.BIN ==========

    def load_snmsgs(self, extra: dict | None = None) -> dict:
        """从缓存目录加载并解析 SNMSG.BIN

        Args:
            extra: 文本映射字典（默认 SNMSG_TEXT_EXTRA），传给 codec 解码

        Returns:
            解析后的消息数据 dict

        Raises:
            FileNotFoundError: 文件不存在
        """
        if extra is None:
            extra = SNMSG_TEXT_EXTRA
        path = os.path.join(self.cache_dir, self._FILE_PATHS["snmsgs"])
        if not os.path.isfile(path):
            raise FileNotFoundError(f"SNMSG.BIN not found: {path}")

        with open(path, "rb") as f:
            raw = f.read()

        data = snmsg_bin.parse(bytearray(raw), extra=extra)
        self._data["snmsgs"] = data
        return data

    def save_snmsgs(self, extra: dict | None = None) -> None:
        """将消息数据构建并写回缓存目录下的 SNMSG.BIN

        Args:
            extra: 文本映射字典（默认 SNMSG_TEXT_EXTRA），传给 codec 编码

        Raises:
            KeyError: 尚未加载消息数据
        """
        if extra is None:
            extra = SNMSG_TEXT_EXTRA
        data = self._data.get("snmsgs")
        if data is None:
            raise KeyError("No SNMSG data loaded. Call load_snmsgs() first.")

        raw = snmsg_bin.build(data, extra=extra)

        path = os.path.join(self.cache_dir, self._FILE_PATHS["snmsgs"])
        with open(path, "wb") as f:
            f.write(raw)

    # ========== 测试用数据导出 ==========

    def dump_to_txt(self, output_dir: str = "_test_cache") -> None:
        """将全部已加载数据导出为 TXT（测试/调试用）

        遍历 _data 中所有条目，以 pprint 格式逐文件写入 output_dir，
        文件名取 _FILE_PATHS 对应的基名。

        Args:
            output_dir: 输出目录路径，默认为项目根下的 _test_cache
        """
        import pprint

        os.makedirs(output_dir, exist_ok=True)

        for key in self._data:
            data = self._data[key]
            basename = os.path.splitext(os.path.basename(self._FILE_PATHS[key]))[0]
            fname = basename + ".txt"
            path = os.path.join(output_dir, fname)

            with open(path, "w", encoding="utf-8") as f:
                f.write(f"# {self._FILE_PATHS[key]}\n")
                f.write(f"# 条目数: {data.get('count', '?')}\n\n")
                f.write(pprint.pformat(data, indent=2, width=120, sort_dicts=False))
                f.write("\n")

            print(f"  [INFO] {fname} 已导出")
