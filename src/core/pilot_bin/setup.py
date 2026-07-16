"""
PILOT.BIN C 扩展构建配置

编译 _pilot_bin C 扩展，静态链接 codec 模块。
"""

from setuptools import Extension, setup

module = Extension(
    "_pilot_bin",
    sources=[
        "pilot_bin.c",
        "../codec/codec.c",
    ],
    include_dirs=[".."],
    define_macros=[("CODEC_AS_SUBMODULE", None)],
)

setup(
    name="pilot_bin",
    version="0.1.0",
    description="PILOT.BIN parser/builder for Super Robot Wars Alpha ROM Editor",
    ext_modules=[module],
)
