"""
空壳 SpinBox — 与 qfluentwidgets SpinBox 同名以匹配 QSS 选择器

仅继承 QSpinBox，不引入 SpinBoxBase/InlineSpinBoxBase 的 hBoxLayout/按钮。
供表格编辑器等需要 SpinBox QSS 主题但不需要内置按钮的场景使用。
"""

from PySide6.QtWidgets import QSpinBox as _QSpinBox


class SpinBox(_QSpinBox):
    """空壳 SpinBox — 仅用于让 qfluentwidgets QSS SpinBox 选择器匹配 MRO"""
    pass
