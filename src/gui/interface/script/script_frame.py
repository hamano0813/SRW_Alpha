"""
剧本编辑框架

继承 ProxyFrame，作为幕间编辑主界面占位。

Classes:
    ScriptFrame: 幕间编辑框架
"""

from PySide6.QtWidgets import QVBoxLayout

from gui.widget import ProxyFrame


class ScriptFrame(ProxyFrame):
    """幕间编辑框架 - 占位"""

    def __init__(self, fields, parent=None):
        """初始化幕间编辑框架

        Args:
            fields: FieldMapping 字段映射实例
            parent: 父 QWidget
        """
        super().__init__(parent)
        self.setObjectName("ScriptFrame")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
