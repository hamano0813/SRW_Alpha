"""
机体编辑框架模块

提供机体数据的表格展示和编辑界面，配合 ROBOT.RAF 解析模块使用。
包含机体主列表和武器子列表的联动显示。

Classes:
    RobotFrame: 机体编辑框架
"""

from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout
from qfluentwidgets import FlowLayout

from gui.custom.proxy_frame import ProxyFrame
from gui.robot.unit_frame import UnitFrame


class RobotFrame(ProxyFrame):
    """机体编辑框架 - 机体主列表 + 武器子列表联动"""

    def __init__(
        self,
        fields,
        parent=None,
    ):
        """初始化机体编辑框架

        Args:
            fields: FieldMapping 字段映射实例
            parent: 父 QWidget
        """
        super().__init__(parent)
        self.setObjectName("RobotFrame")

        self._rom_data: dict | None = None

        # ========== 机体主表 ==========

        self._unit_frame = UnitFrame()
        self._unit_frame.set_field(fields)

        # ========== 布局 ==========

        main_layout = QHBoxLayout(self)
        right_layout = QVBoxLayout()
        right_top_layout = FlowLayout()
        right_bottom_layout = QHBoxLayout()
        right_layout.addLayout(right_top_layout)
        right_layout.addLayout(right_bottom_layout)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._unit_frame)
        main_layout.addLayout(right_layout, 1)
        main_layout.addStretch()  # [TODO] 当右侧面板有控件时拆除

        self.setLayout(main_layout)

        from pprint import pprint

        self._unit_frame.sClicked.connect(lambda x, y: pprint(y, depth=1))  # [TODO]

    # ========== 数据解析 ==========

    def set_rom_data(self, data: dict) -> None:
        """装入 ROM 的机体数据

        Args:
            data: Rom().parse_robots() 返回的 dict，
                  包含 "robots" 列表
        """
        self._rom_data = data
        robots = data.get("robots", [])
        self._unit_frame.set_data(robots["robots"])
