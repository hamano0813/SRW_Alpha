"""
SNMSG.BIN 解析器包装

对外暴露 C 扩展的 parse / build 接口。

Functions:
    parse: 解析 SNMSG.BIN 二进制数据
    build: 构建 SNMSG.BIN 二进制数据
"""

from ._snmsg_bin import parse, build

__all__ = ["parse", "build"]
