"""
多行文本编辑器 — 继承 QPlainTextEdit + TableEditor，自绘透明背景

与 SingleLineEdit 对应，使用 QPlainTextEdit 实现多行文本编辑。
适用于表格中需换行显示的字段。由表格 delegate 控制形状和圆角。

Classes:
    MultiLineEdit: 多行文本编辑器
"""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QTextCursor
from PySide6.QtWidgets import QPlainTextEdit, QFrame
from qfluentwidgets import isDarkTheme

from .table_editor import TableEditor


class MultiLineEdit(QPlainTextEdit, TableEditor):
    """多行文本编辑器 — 透明背景 + 纯文字绘制 + TableEditor 数据协议

    无边框、无焦点指示线，仅通过 palette 控制文字颜色。
    获得焦点时光标自动定位到末尾。
    """

    def __init__(self, parent=None):
        """初始化多行文本编辑器

        Args:
            parent: 父 QWidget
        """
        QPlainTextEdit.__init__(self, parent)
        TableEditor.__init__(self, parent)

        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setStyleSheet("background: transparent;")

        self.textChanged.connect(self._on_text_changed)

    def focusInEvent(self, e):
        """获得焦点时光标定位到末尾，不选中全文

        Args:
            e: 焦点事件
        """
        super().focusInEvent(e)
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)

    # ========== 主题色 ==========

    def _text_color(self) -> QColor:
        """根据当前主题返回对应的文字颜色"""
        return QColor(255, 255, 255) if isDarkTheme() else QColor(0, 0, 0)

    # ========== 绘制 ==========

    def paintEvent(self, e):
        """仅设置文字颜色，由 QPlainTextEdit 完成透明背景绘制

        Args:
            e: 绘制事件
        """
        palette = self.palette()
        palette.setColor(palette.ColorRole.Text, self._text_color())
        self.setPalette(palette)
        QPlainTextEdit.paintEvent(self, e)

    # ========== TableEditor 数据协议 ==========

    def set_value(self, value) -> None:
        """存入文本值并刷新显示

        Args:
            value: 字符串文本
        """
        TableEditor.set_value(self, value)

    def get_value(self) -> str:
        """返回当前文本值"""
        return self._value if self._value is not None else ""

    def format_value(self) -> None:
        """将 _value 同步到显示，光标定位到末尾"""
        self.blockSignals(True)
        self.setPlainText(str(self._value) if self._value is not None else "")
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.setTextCursor(cursor)
        self.blockSignals(False)

    def apply_font(self, font: QFont) -> None:
        """将字体应用到编辑器

        Args:
            font: 要应用的 QFont
        """
        self.setFont(font)

    def is_valid(self, value) -> bool:
        """校验值是否为字符串类型

        Args:
            value: 待校验的值

        Returns:
            True 为字符串类型
        """
        return isinstance(value, str)

    def format_display(self, value) -> str:
        """将值格式化为显示文本

        Args:
            value: 原始值

        Returns:
            显示文本
        """
        return str(value) if value is not None else ""

    # ========== 内部槽 ==========

    def _on_text_changed(self) -> None:
        """用户输入时同步 _value 并发射 dataChanged"""
        self._value = self.toPlainText()
        self.dataChanged.emit(self._value)
