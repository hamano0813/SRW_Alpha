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
