"""
表格编辑器 — 继承 QLineEdit + CellEditor，自绘透明背景

集 QLineEdit 的文本编辑与 CellEditor 的数据协议于一身，
不再需要额外的 LineTextWidget 包装层。
适用于表格任意列（形状由表格 delegate 的背景圆角决定）。

Classes:
    CellSingleLine: 表格编辑器
"""

from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QLineEdit
from qfluentwidgets import setCustomStyleSheet

from .cell_editor import CellEditor


class CellSingleLine(QLineEdit, CellEditor):
    """表格编辑器 — 透明背景 + CellEditor 数据协议

    无边框、无焦点指示线，文字颜色由 setCustomStyleSheet 跟随主题切换。
    获得焦点时光标自动定位到末尾。
    """

    def __init__(self, parent=None):
        """初始化表格编辑器

        Args:
            parent: 父 QWidget
        """
        QLineEdit.__init__(self, parent)
        CellEditor.__init__(self, parent)

        self.setFrame(False)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        # QSS color 控制文字和光标颜色，setCustomStyleSheet 自动跟随主题
        setCustomStyleSheet(self,
            "background: transparent; color: #000000;",
            "background: transparent; color: #FFFFFF;")

        self.textChanged.connect(self._on_text_changed)

    def focusInEvent(self, e):
        """获得焦点时光标定位到末尾，不选中全文

        Args:
            e: 焦点事件
        """
        super().focusInEvent(e)
        self.setCursorPosition(len(self.text()))

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

    def _on_text_changed(self, text: str) -> None:
        """用户输入时同步 _value 并发射 dataChanged"""
        self._value = text
        self.dataChanged.emit(self._value)
