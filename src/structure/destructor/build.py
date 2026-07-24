#!/usr/bin/env python
# -*- coding: utf-8 -*-

import setuptools

setuptools.setup(
    name="DataParser",
    version="0.1.0",
    author="Hamano0813",
    description="机战α数据解析",
    packages=setuptools.find_packages(),
    ext_modules=[
        setuptools.Extension("LZSS", [
            "compressor\\lzss.c",
        ]),
        setuptools.Extension("ROBOT", [
            "parser\\util.c",
            "parser\\robot.c",
        ]),
        setuptools.Extension("SNMSG", [
            "parser\\util.c",
            "parser\\snmsg.c",
        ]),
        setuptools.Extension("SNDATA", [
            "parser\\util.c",
            "parser\\sndata.c",
        ]),
        setuptools.Extension("SCRIPT", [
            "parser\\util.c",
            "parser\\script.c",
        ]),
    ],
)
