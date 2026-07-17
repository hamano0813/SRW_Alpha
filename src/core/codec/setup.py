"""
Codec C 扩展构建配置

编译 _codec.pyd，Shift-JIS X0213 编解码器，无外部依赖。
"""

from setuptools import Extension, setup

module = Extension(
    "_codec",
    sources=["codec.c"],
)

setup(
    name="codec",
    version="0.1.0",
    description="Shift-JIS x0213 codec for Super Robot Wars Alpha ROM Editor",
    ext_modules=[module],
)
