"""
LZSS 压缩算法包装

对外暴露 C 扩展的 compress / decompress 接口。

Functions:
    compress: LZSS 压缩
    decompress: LZSS 解压
"""

from ._lzss import compress, decompress

__all__ = ["compress", "decompress"]
