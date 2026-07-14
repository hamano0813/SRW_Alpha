"""
SNDATA.BIN C 扩展构建配置
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
