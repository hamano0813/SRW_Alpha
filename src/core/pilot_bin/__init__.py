"""
pilot_bin — PILOT.BIN 解析/构建模块

提供 PILOT.BIN 的 parse/build 接口，底层由 _pilot_bin C 扩展实现。

Classes:
    parse: 解析 PILOT.BIN 二进制 → Python dict
    build: 从 Python dict 重建 PILOT.BIN 二进制
"""

from ._pilot_bin import parse, build

__all__ = ["parse", "build"]
