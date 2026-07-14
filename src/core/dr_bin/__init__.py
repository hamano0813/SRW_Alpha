"""
dr_bin — DR.BIN 解析/构建模块

提供 DR.BIN 的 parse/build 接口，底层由 _dr_bin C 扩展实现。
"""

from ._dr_bin import build, parse

__all__ = ["parse", "build"]
