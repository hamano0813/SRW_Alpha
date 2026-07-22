"""
StretchLabel BodyLabel子类 - 水平拉伸填充剩余空间

默认水平策略为 Expanding，在有富余宽度时会尽量吃满分配的空间。
适合作为网格布局中的标签使用，无需再手动设置 minWidth/fixedWidth。

Classes:
    StretchLabel: 水平拉伸标签
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy
from qfluentwidgets import BodyLabel


class StretchLabel(BodyLabel):
    """水平拉伸标签 - 默认尽量吃满分配的水平空间"""

    def __init__(self, text: str = "", parent=None):
        """初始化水平拉伸标签

        Args:
            text:   标签文本
            parent: 父 QWidget
        """
        super().__init__(text)
        if parent is not None:
            self.setParent(parent)
        self.setMinimumWidth(70)
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Preferred,
        )
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
