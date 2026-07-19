"""
SNDATA.BIN 解析/构建模块

提供对 SNDATA.BIN 场景数据文件的解析与构建功能。
二进制结构：
  - 0x200 × UINT32 场景指针表（前 0x8C 个有效）
  - 0x8C × SCENARIO（每个 0x4048B 定长）

Classes:
    (none, C extension with parse/build functions)
"""

from ._sndata import build, parse

__all__ = ["build", "parse"]
