"""
抽象基础组件 - 供 widget 层内部组合使用

不直接暴露给卡片层，由 common/special 控件在内部继承复用。

Classes:
    VerticalSpinBox: 垂直微调框基类
"""

from .spin_box import VerticalSpinBox
