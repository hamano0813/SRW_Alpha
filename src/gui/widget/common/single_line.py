"""
单行文本输入框 - 面板通用版本

继承 LineEdit，提供 set_value / value / valueChanged 信号槽接口。
适用于卡片面板中的文本输入，封装统一的样式和尺寸。

Classes:
    CommonSingleLine: 单行文本输入框
"""

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from qfluentwidgets import LineEdit


class CommonSingleLine(LineEdit):
    """单行文本输入框 - 面板通用版本"""

    valueChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(33)
        self.setStyleSheet("LineEdit { padding-left: 10px; }")
        self.textChanged.connect(self.valueChanged)

    def set_value(self, value: str) -> None:
        """存入文本值并刷新显示

        Args:
            value: 文本内容
        """
        self.blockSignals(True)
        self.setText(str(value) if value else "")
        self.blockSignals(False)

    def value(self) -> str:
        """返回当前文本值"""
        return self.text()

    def apply_font(self, font: QFont | dict) -> None:
        """应用字体

        Args:
            font: QFont 或字体配置字典
        """
        if isinstance(font, dict):
            qfont = QFont()
            for k in ("family", "size", "weight", "italic"):
                v = font.get(k)
                if v:
                    getattr(qfont, f"set{k.capitalize()}")(v)
            font = qfont
        self.setFont(font)
