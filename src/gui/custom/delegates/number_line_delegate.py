"""
数值列委托 - 配合 NumberLineEdit 使用

每列一个委托实例，通过 setItemDelegateForColumn 绑定。
与 SingleLineDelegate 类似，但编辑器仅接受数值输入并右对齐。

Classes:
    NumberLineEditDelegate: 数值列委托
"""

from typing import Any

from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QStyleOptionViewItem, QWidget

from gui.custom.widgets import NumberLineEdit

from .base_delegate import DataWidgetDelegate


class NumberLineEditDelegate(DataWidgetDelegate):
    """数值列委托 - 编辑器为 NumberLineEdit"""

    widget_class = NumberLineEdit

    def __init__(self, font: QFont | dict | None = None, parent=None):
        """初始化数值列委托

        Args:
            font: 编辑器字体，QFont 实例或字体属性字典
            parent: 父对象
        """
        super().__init__(parent=parent, font=font)

    # ========== 编辑器几何 ==========

    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """将编辑器位置设为单元格区域，上下清零"""
        rect = option.rect.adjusted(3, 0, 0, 0)
        editor.setGeometry(rect)
        editor.setFixedHeight(rect.height())

    # ========== 格式化 ==========

    def format_display(self, value) -> str:
        """将原始值格式化为数值文本

        Args:
            value: 原始值

        Returns:
            数值字符串
        """
        return str(value) if value is not None else ""

    def parse_display(self, text: str) -> Any:
        """将显示文本解析为数值

        Args:
            text: 数字字符串

        Returns:
            整数值
        """
        try:
            return int(text)
        except (ValueError, TypeError):
            return 0
