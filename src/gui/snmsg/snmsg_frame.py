"""
消息编辑框架模块

提供消息数据的表格展示和编辑界面，配合 MESSAGE 解析模块使用。
包含消息列表子框架，结构比 RobotFrame 简单（无右侧面板）。

Classes:
    SnmsgFrame: 消息编辑框架
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QVBoxLayout

from gui.custom.proxy_frame import ProxyFrame
from gui.snmsg.msg_frame import MsgFrame


class SnmsgFrame(ProxyFrame):
    """消息编辑框架 - 消息主列表（可扩展右侧面板）"""

    sClicked = Signal(int, dict)

    def __init__(self, fields, parent=None):
        """初始化消息编辑框架

        Args:
            fields: FieldMapping 字段映射实例
            parent: 父 QWidget
        """
        super().__init__(parent)
        self.setObjectName("MessageFrame")

        self._rom_data: dict | None = None

        # ========== 消息主表 ==========

        self._msg_frame = MsgFrame()
        self._msg_frame.set_field(fields)
        self._msg_frame.sClicked.connect(self.sClicked.emit)

        # ========== 布局 ==========

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._msg_frame)

        self.setLayout(layout)

    # ========== 数据解析 ==========

    def set_rom_data(self, data: dict) -> None:
        """装入 ROM 的消息数据

        取 snmsgs 列表填入主表格。

        Args:
            data: Rom().parse_messages() 返回的 dict
        """
        self._rom_data = data
        snmsgs_data = data.get("snmsgs", {})
        self._msg_frame.set_data(snmsgs_data.get("snmsgs", []))
