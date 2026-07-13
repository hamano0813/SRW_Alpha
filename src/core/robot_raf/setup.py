from setuptools import Extension, setup

module = Extension(
    "_robot_raf",
    sources=[
        "robot_raf.c",
        "../lzss/lzss.c",
    ],
    include_dirs=[".."],
)

setup(
    name="robot_raf",
    version="0.1.0",
    description="ROBOT.RAF parser/builder for Super Robot Wars Alpha ROM Editor",
    ext_modules=[module],
)
