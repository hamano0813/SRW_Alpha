"""
SNDATA.BIN C 扩展构建配置

编译 _sndata C 扩展，无外部依赖（纯二进制，无文本编码）。
"""

from setuptools import Extension, setup

module = Extension(
    "_sndata",
    sources=["sndata_bin.c"],
)

setup(
    name="_sndata",
    version="1.0",
    description="SNDATA.BIN parser/builder",
    ext_modules=[module],
)
