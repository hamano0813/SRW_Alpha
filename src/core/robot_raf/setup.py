from setuptools import Extension, setup

module = Extension(
    "_robot_raf",
    sources=[
        "robot_raf.c",
        "../lzss/lzss.c",
        "../codec/codec.c",
    ],
    include_dirs=[".."],
    define_macros=[("CODEC_AS_SUBMODULE", None)],
)

setup(
    name="robot_raf",
    version="0.1.0",
    description="ROBOT.RAF parser/builder for Super Robot Wars Alpha ROM Editor",
    ext_modules=[module],
)
