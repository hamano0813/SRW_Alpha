"""
dc_bin — DC.BIN 解析/构建模块

提供 DC.BIN 的 parse/build 接口，底层由 _dc_bin C 扩展实现。
"""

from ._dc_bin import build, parse

__all__ = ["parse", "build"]
