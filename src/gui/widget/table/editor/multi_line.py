"""
多行文本编辑器 — 继承 QPlainTextEdit + CellEditor，自绘透明背景

与 CellSingleLine 对应，使用 QPlainTextEdit 实现多行文本编辑。
适用于表格中需换行显示的字段。由表格 delegate 控制形状和圆角。

Classes:
    CellMultiLine: 多行文本编辑器
"""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QTextCursor
from PySide6.QtWidgets import QFrame, QPlainTextEdit
from qfluentwidgets import isDarkTheme

from .cell_editor import CellEditor


class CellMultiLine(QPlainTextEdit, CellEditor):
    """多行文本编辑器 — 透明背景 + 纯文字绘制 + CellEditor 数据协议

    无边框、无焦点指示线，仅通过 palette 控制文字颜色。
    获得焦点时光标自动定位到末尾。
    """

    def __init__(self, parent=None, max_lines: int = 0):
        """初始化多行文本编辑器

        Args:
            parent: 父 QWidget
            max_lines: 最大行数，0 表示不限，3 表示最多 3 行（即 2 个换行符）
        """
        QPlainTextEdit.__init__(self, parent)
        CellEditor.__init__(self, parent)

        self._max_lines: int = max_lines

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

    # ========== 键盘事件 ==========

    def keyPressEvent(self, e):
        """拦截回车键，已达行数上限时不响应

        Args:
            e: 键盘事件
        """
        if self._max_lines > 0 and e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            max_nl = self._max_lines - 1
            if self.toPlainText().count("\n") >= max_nl:
                return  # 已达上限，忽略回车
        super().keyPressEvent(e)

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

    # ========== CellEditor 数据协议 ==========

    def set_value(self, value) -> None:
        """存入文本值并刷新显示

        Args:
            value: 字符串文本
        """
        CellEditor.set_value(self, value)

    def get_value(self) -> str:
        """返回当前文本值"""
        return self._value if self._value is not None else ""

    def format_value(self) -> None:
        """将 _value 同步到显示，光标定位到末尾"""
        text = str(self._value) if self._value is not None else ""
        text = self._truncate_newlines(text)
        self._value = text
        self.blockSignals(True)
        self.setPlainText(text)
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

    # ========== 行数限制 ==========

    def _truncate_newlines(self, text: str) -> str:
        """将文本截断至行数上限，超出部分丢弃

        Args:
            text: 原始文本

        Returns:
            截断后的文本，不超过 _max_lines 行
        """
        if self._max_lines <= 0:
            return text
        max_nl = self._max_lines - 1
        if text.count("\n") <= max_nl:
            return text
        # 找到第 (max_nl+1) 个换行符，在此截断
        pos = -1
        for _ in range(max_nl + 1):
            pos = text.index("\n", pos + 1)
        return text[:pos]

    # ========== 内部槽 ==========

    def _on_text_changed(self) -> None:
        """用户输入时同步 _value 并发射 dataChanged

        输入时回车键已被 keyPressEvent 拦截，此处仅作为粘贴等操作的防护截断。
        """
        text = self.toPlainText()
        text = self._truncate_newlines(text)
        if text != self.toPlainText():
            self.blockSignals(True)
            self.setPlainText(text)
            cursor = self.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.setTextCursor(cursor)
            self.blockSignals(False)
            self._value = text
            self.dataChanged.emit(self._value)
            return
        self._value = text
        self.dataChanged.emit(self._value)
