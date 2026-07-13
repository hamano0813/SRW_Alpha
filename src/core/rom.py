"""
ROM 数据核心调度类

作为 ROM 编辑器的数据中枢，管理所有已解析的 ROM 数据，
并提供对各个文件模块（ROBOT.RAF 等）的统一读写调度。
缓存路径从 config 模块自动获取。

Classes:
    Rom: ROM 数据核心调度类
"""

import os

import config

from . import robot_raf


class Rom:
    """ROM 数据核心调度类 - 存储已加载的 ROM 数据并提供文件读写接口"""

    # 各文件在缓存目录下的相对路径（因游戏 ISO 结构固定而写死）
    _FILE_PATHS: dict[str, str] = {
        "robots": "UNITPRAM/ROBOT.RAF",
    }

    # 文件 key → 对应的方法名（read_cache / write_cache 通过此表分发）
    _LOAD_DISPATCH: dict[str, str] = {
        "robots": "load_robots",
    }
    _SAVE_DISPATCH: dict[str, str] = {
        "robots": "save_robots",
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
        """读取并解析缓存目录下所有已注册的数据文件

        遍历 _LOAD_DISPATCH 并逐一调用对应的 load_* 方法。

        Raises:
            FileNotFoundError: 缓存目录不存在
        """
        if not os.path.isdir(self.cache_dir):
            raise FileNotFoundError(f"Cache directory not found: {self.cache_dir}")

        for method_name in self._LOAD_DISPATCH.values():
            getattr(self, method_name)()

    def write_cache(self) -> None:
        """将所有已修改的数据构建并写回缓存目录

        遍历 _data 中已存在的 key，通过 _SAVE_DISPATCH 分发到 save_* 方法。
        """
        for key in self._data:
            method_name = self._SAVE_DISPATCH.get(key)
            if method_name is None:
                continue
            getattr(self, method_name)()

    # ========== ROBOT.RAF 单文件读写 ==========

    def load_robots(self) -> dict:
        """从缓存目录加载并解析 ROBOT.RAF

        Returns:
            解析后的机体数据 dict

        Raises:
            FileNotFoundError: 文件不存在
            RuntimeError: 解析/解压失败
        """
        path = os.path.join(self.cache_dir, self._FILE_PATHS["robots"])
        if not os.path.isfile(path):
            raise FileNotFoundError(f"ROBOT.RAF not found: {path}")

        with open(path, "rb") as f:
            raw = f.read()

        data = robot_raf.parse(raw)
        self._data["robots"] = data
        return data

    def save_robots(self) -> None:
        """将机体数据构建并写回缓存目录下的 ROBOT.RAF

        Raises:
            KeyError: 尚未加载机体数据
            RuntimeError: 构建/压缩失败
        """
        data = self._data.get("robots")
        if data is None:
            raise KeyError("No robot data loaded. Call load_robots() first.")

        raw = robot_raf.build(data)

        path = os.path.join(self.cache_dir, self._FILE_PATHS["robots"])
        with open(path, "wb") as f:
            f.write(raw)
