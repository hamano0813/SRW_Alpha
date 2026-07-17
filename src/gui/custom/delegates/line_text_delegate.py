"""
单行文本列委托 - 配合 LineTextWidget 使用

每列一个委托实例，通过 setItemDelegateForColumn 绑定。

Classes:
    LineTextDelegate: 单行文本列委托
"""

from PySide6.QtGui import QFont

from gui.custom.widgets import LineTextWidget

from .base_delegate import DataWidgetDelegate


class LineTextDelegate(DataWidgetDelegate):
    """单行文本列委托 - 编辑器为 LineTextWidget"""

    widget_class = LineTextWidget

    def __init__(self, font: QFont | dict | None = None, parent=None):
        """初始化单行文本列委托

        Args:
            font: 编辑器字体，QFont 实例或字体属性字典
            parent: 父对象
        """
        super().__init__(parent=parent, font=font)
