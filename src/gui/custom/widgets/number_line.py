"""
数值编辑器 — 继承 QLineEdit + DataWidget，只允许数值输入

右对齐、仅输入整数、透明背景，与 SingleLineEdit 风格一致。

Classes:
    NumberLine: 数值编辑器
"""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QIntValidator
from PySide6.QtWidgets import QLineEdit
from qfluentwidgets import isDarkTheme

from .data_widget import DataWidget


class NumberLine(QLineEdit, DataWidget):
    """数值编辑器 — 透明背景 + 右对齐 + 仅数值输入

    无边框、无焦点指示线，仅通过 palette 控制文字颜色。
    获得焦点时自动选中全文。
    """

    def __init__(self, parent=None):
        """初始化数值编辑器

        Args:
            parent: 父 QWidget
        """
        QLineEdit.__init__(self, parent)
        DataWidget.__init__(self, parent)

        self.setFrame(False)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.setValidator(QIntValidator())
        self.setStyleSheet(
            "QLineEdit { padding-left: 14px; padding-top: 1px; padding-bottom: 1px; background: transparent; }"
        )

        self.textChanged.connect(self._on_text_changed)

    def focusInEvent(self, e):
        """获得焦点时选中全文"""
        super().focusInEvent(e)
        self.selectAll()

    # ========== 主题色 ==========

    def _text_color(self) -> QColor:
        """文字颜色"""
        return QColor(255, 255, 255) if isDarkTheme() else QColor(0, 0, 0)

    # ========== 绘制 ==========

    def paintEvent(self, e):
        """仅设置文字颜色，由 QLineEdit 完成透明背景绘制"""
        palette = self.palette()
        palette.setColor(palette.ColorRole.Text, self._text_color())
        self.setPalette(palette)
        QLineEdit.paintEvent(self, e)

    # ========== DataWidget 数据协议 ==========

    def set_value(self, value) -> None:
        """存入数值并刷新显示

        Args:
            value: 整数或数字字符串
        """
        DataWidget.set_value(self, value)

    def get_value(self) -> str:
        """返回当前文本值"""
        return self._value if self._value is not None else ""

    def format_value(self) -> None:
        """将 _value 同步到显示"""
        self.blockSignals(True)
        self.setText(str(self._value) if self._value is not None else "")
        self.setCursorPosition(len(self.text()))
        self.blockSignals(False)

    def apply_font(self, font: QFont) -> None:
        """将字体应用到编辑器

        Args:
            font: 要应用的 QFont
        """
        self.setFont(font)

    def is_valid(self, value) -> bool:
        """校验值是否为可接受的数值格式"""
        if value is None:
            return False
        try:
            int(str(value))
            return True
        except (ValueError, TypeError):
            return False

    def format_display(self, value) -> str:
        """将值格式化为显示文本"""
        return str(value) if value is not None else ""

    # ========== 内部槽 ==========

    def _on_text_changed(self, text: str) -> None:
        """用户输入时同步 _value 并发射 dataChanged"""
        self._value = text
        self.dataChanged.emit(self._value)
