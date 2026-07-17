"""
中间列单行文本委托 - 配合 LineTextMidWidget 使用

每列一个委托实例，通过 setItemDelegateForColumn 绑定。

Classes:
    LineTextMidDelegate: 中间列单行文本委托
"""

from PySide6.QtGui import QFont

from gui.custom.widgets import LineTextMidWidget

from .base_delegate import DataWidgetDelegate


class LineTextMidDelegate(DataWidgetDelegate):
    """中间列单行文本委托 - 编辑器为 LineTextMidWidget"""

    widget_class = LineTextMidWidget

    def __init__(self, font: QFont | dict | None = None, parent=None):
        """初始化中间列单行文本委托

        Args:
            font: 编辑器字体，QFont 实例或字体属性字典
            parent: 父对象
        """
        super().__init__(parent=parent, font=font)
