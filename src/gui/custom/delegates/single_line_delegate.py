"""
单行文本列委托 - 配合 SingleLineEdit 使用

每列一个委托实例，通过 setItemDelegateForColumn 绑定。

Classes:
    SingleLineDelegate: 单行文本列委托
"""

from typing import Any

from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QStyleOptionViewItem, QWidget

from gui.custom.widgets import SingleLineEdit

from .base_delegate import DataWidgetDelegate


class SingleLineDelegate(DataWidgetDelegate):
    """单行文本列委托 - 编辑器为 SingleLineEdit"""

    widget_class = SingleLineEdit

    def __init__(self, font: QFont | dict | None = None, parent=None):
        """初始化单行文本列委托

        Args:
            font: 编辑器字体，QFont 实例或字体属性字典
            parent: 父对象
        """
        super().__init__(parent=parent, font=font)

    # ========== 编辑器几何 ==========

    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """将编辑器位置设为单元格区域，上下各缩 1px 并锁定高度

        Args:
            editor: SingleLineEdit 实例
            option: 样式选项
            index: 单元格索引
        """
        rect = option.rect.adjusted(3, 0, 0, 0)
        editor.setGeometry(rect)
        editor.setFixedHeight(rect.height())

    # ========== 格式化 ==========

    def format_display(self, value) -> str:
        """将原始值格式化为显示文本

        Args:
            value: 原始值

        Returns:
            显示文本
        """
        return str(value) if value is not None else ""

    def parse_display(self, text: str) -> Any:
        """将显示文本解析为原始值

        Args:
            text: 显示文本

        Raises:
            NotImplementedError: 单行文本不支持反解析
        """
        raise NotImplementedError(
            f"{type(self).__name__} does not implement parse_display"
        )
