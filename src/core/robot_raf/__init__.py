"""
ROBOT.RAF 解析器包装

对外暴露 C 扩展的 parse / build 接口。

Functions:
    parse: 解析 ROBOT.RAF 二进制数据
    build: 构建 ROBOT.RAF 二进制数据
"""

from ._robot_raf import parse, build

__all__ = ["parse", "build"]
