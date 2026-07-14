"""
DR.BIN C 扩展构建配置

编译 _dr_bin.pyd，静态链接 lzss 和 codec 子模块。
"""

from setuptools import Extension, setup

module = Extension(
    "_dr_bin",
    sources=[
        "dr_bin.c",
        "../lzss/lzss.c",
        "../codec/codec.c",
    ],
    include_dirs=[".."],
    define_macros=[("CODEC_AS_SUBMODULE", None)],
)

setup(
    name="dr_bin",
    version="0.1.0",
    description="DR.BIN parser/builder for Super Robot Wars Alpha ROM Editor",
    ext_modules=[module],
)
