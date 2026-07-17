"""
Shift-JIS X0213 编解码器包装

对外暴露 C 扩展的 decode / encode / encode_var 接口。

Functions:
    decode: 解码 Shift-JIS 字节为 Python 字符串
    encode: 编码 Python 字符串为 Shift-JIS 字节
    encode_var: 变长编码扩展
"""

from ._codec import decode, encode, encode_var

__all__ = ["decode", "encode", "encode_var"]
