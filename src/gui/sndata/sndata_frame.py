"""
场景数据编辑框架

继承 ProxyFrame，作为场景数据编辑主界面占位。

Classes:
    SndataFrame: 场景数据编辑框架
"""

from PySide6.QtWidgets import QVBoxLayout

from gui.custom.proxy_frame import ProxyFrame


class SndataFrame(ProxyFrame):
    """场景数据编辑框架 - 占位"""

    def __init__(self, fields, parent=None):
        """初始化音乐数据编辑框架

        Args:
            fields: FieldMapping 字段映射实例
            parent: 父 QWidget
        """
        super().__init__(parent)
        self.setObjectName("SndataFrame")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
