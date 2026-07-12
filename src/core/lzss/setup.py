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
