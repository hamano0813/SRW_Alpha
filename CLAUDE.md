# SRW Alpha ROM Editor — 项目规范

## Python 注释风格

### 1. 模块头（文件顶部）

所有 `.py` 文件必须包含模块头 docstring，格式如下：

```python
"""
模块简短描述（一句话）

模块详细说明。说明该模块提供什么功能、给谁用。
可换行说明设计用途。

Classes:
    ClassName: 一句话说明
"""
```

### 2. 类文档字符串

每个类必须有 docstring：

```python
class ClassName(ParentClass):
    """类简短描述 - 可选细化说明"""
```

### 3. 方法文档字符串

- **公开方法**：使用 `""" """` docstring，遵循以下格式
- **私有方法**：至少一句中文说明，省略 Args/Returns 如果一目了然

```python
def method_name(self, param1: str, param2: int) -> bool:
    """方法一句话描述

    可选详细说明：什么时候调用、有什么副作用。

    Args:
        param1: 参数说明
        param2: 参数说明

    Returns:
        返回值说明
    """
```

### 4. 行内 `#` 注释

- 统一使用**中文**注释
- 优先写"为什么这么做"的设计意图，而不是"代码在做什么"
- 代码本身已表达清楚的，不加注释
- 格式：`# 注释内容`（井号后加一个空格）

### 5. 段落分隔

长方法或模块内的段落用分隔线：

```python
# ========== 段落标题 ==========
```

### 6. 禁止

- 禁止在方法体内的 `if`/`else` 分支内写 docstring（应移到方法顶部）
- 禁止中英文混用注释
- 禁止冗余的"翻译式"注释（如 `self.titleLabel.setText(text)  # 设置标题文本`）

## ROM 模块规范

### Rom 类设计模式

`core/rom.py` 的 `Rom` 类作为数据中枢，采用三层配置管理各文件类型：

```python
_FILE_PATHS: dict[str, str] = {
    "robots": "UNITPRAM/ROBOT.RAF",
}
_LOAD_DISPATCH: dict[str, str] = {
    "robots": "load_robots",
}
_SAVE_DISPATCH: dict[str, str] = {
    "robots": "save_robots",
}
```

- `_FILE_PATHS` — 文件 key → 缓存目录下的相对路径
- `_LOAD_DISPATCH` — 文件 key → `load_*` 方法名（供 `read_cache()` 分发）
- `_SAVE_DISPATCH` — 文件 key → `save_*` 方法名（供 `write_cache()` 分发）

新增文件类型时需同步更新上述三个字典并添加对应的 `load_*` / `save_*` 方法。

## 测试文件规范

`tests/` 下的测试文件遵循以下风格：

```python
"""
模块简短描述

测试内容：
  1. ...
  2. ...
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


def main() -> int:
    """执行测试并返回退出码"""
    # ...
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
```

- 模块头 docstring 列出测试点
- `main()` 返回 int（0=通过，1=失败）
- 通过 `sys.exit(main())` 退出

## C 扩展规范

`src/core/*/` 下的 C 模块遵循以下模式：

### 目录结构

```
src/core/<module>/
├── <module>.c          # C 扩展源码
├── <module>.pyi        # 类型存根
├── __init__.py          # Python 包装（from ._<module> import ...）
├── setup.py             # setuptools 构建配置
├── setup.cfg            # 编译器配置（mingw32）
└── README.md            # 数据结构和 API 文档
```

### API 设计

C 扩展对外暴露对称的 parse/build 接口：

- `parse(data: bytes | bytearray) -> dict` — 二进制 → Python 对象
- `build(data: dict) -> bytearray` — Python 对象 → 二进制

内部按两层拆分（以 robot_raf.c 为例）：

```
第一层（纯二进制，不碰 Python 对象）：
  _entries_decompress()  — 原始文件 → 中间态（解压 + 拼接）
  _entries_compress()    — 中间态 → 原始文件（拆分 + 压缩）

第二层（在 parse/build 中内联）：
  _destruct_*()          — 中间态 → Python dict（字段移位拆包）
  _structure_*()         — Python dict → 中间态（字段移位打包）
```

第一层与第二层独立，第一层可复用 LZSS 等基础模块（编译时静态链接 `lzss.c`）。

## 控制台输出标记

终端输出使用方括号标记表示日志等级，字体有特殊连字效果时可清晰显示：

`[INFO]` `[WARN]` `[ERROR]` `[TODO]` `[DEBUG]` `[TRACE]` `[FIXME]` `[NOTE]` `[HACK]` `[MARK]` `[WARNING]`

- 输出约定标记尽在此列表中选取
- 不要使用 `[OK]`（无连字效果，已统一替换为 `[INFO]`）
