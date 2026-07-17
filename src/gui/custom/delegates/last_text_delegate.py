"""
末列单行文本委托 - 配合 LineTextLastWidget 使用

每列一个委托实例，通过 setItemDelegateForColumn 绑定。

Classes:
    LineTextLastDelegate: 末列单行文本委托
"""

from PySide6.QtGui import QFont

from gui.custom.widgets import LineTextLastWidget

from .base_delegate import DataWidgetDelegate


class LineTextLastDelegate(DataWidgetDelegate):
    """末列单行文本委托 - 编辑器为 LineTextLastWidget"""

    widget_class = LineTextLastWidget

    def __init__(self, font: QFont | dict | None = None, parent=None):
        """初始化末列单行文本委托

        Args:
            font: 编辑器字体，QFont 实例或字体属性字典
            parent: 父对象
        """
        super().__init__(parent=parent, font=font)
