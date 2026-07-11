from setuptools import setup, Extension

setup(
    name="lzss",
    ext_modules=[
        Extension(
            "_lzss",
            sources=["lzss.c"],
        ),
    ],
)
