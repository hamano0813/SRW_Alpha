"""
LZSS C 扩展构建配置

编译 _lzss.pyd，纯 LZSS 算法实现，无外部依赖。
"""

from setuptools import Extension, setup

setup(
    name="lzss",
    ext_modules=[
        Extension(
            "_lzss",
            sources=["lzss.c"],
        ),
    ],
)
