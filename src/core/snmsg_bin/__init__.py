"""
snmsg_bin — SNMSG.BIN 解析/构建模块

提供 SNMSG.BIN 的 parse/build 接口，底层由 _snmsg_bin C 扩展实现。

Classes:
    parse: 解析 SNMSG.BIN 二进制 → Python dict
    build: 从 Python dict 重建 SNMSG.BIN 二进制
"""

from ._snmsg_bin import parse, build

__all__ = ["parse", "build"]
