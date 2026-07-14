"""
snmsg_bin C 扩展构建配置

编译 _snmsg_bin.pyd，静态链接 codec 子模块。
"""

from setuptools import Extension, setup

module = Extension(
    "_snmsg_bin",
    sources=[
        "snmsg_bin.c",
        "../codec/codec.c",
    ],
    include_dirs=[".."],
    define_macros=[("CODEC_AS_SUBMODULE", None)],
)

setup(
    name="snmsg_bin",
    version="0.1.0",
    description="SNMSG.BIN parser/builder for Super Robot Wars Alpha ROM Editor",
    ext_modules=[module],
)
