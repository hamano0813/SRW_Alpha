"""
机体编辑框架模块

提供机体数据的表格展示和编辑界面，配合 ROBOT.RAF 解析模块使用。
包含机体主列表和武器子列表的联动显示。

Classes:
    RobotFrame: 机体编辑框架
"""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout
from qfluentwidgets import FlowLayout

from gui.custom import fonts
from gui.custom.models.fixed_model import FixedTableModel
from gui.custom.views.fixed_view import FixedTableView


class RobotFrame(QFrame):
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

        self._robot_model = FixedTableModel()
        self._robot_model.set_font({0: fonts.TEXT_FONT})

        self._rom_data: dict | None = None

        # ========== 机体主表 ==========

        self._robot_view = FixedTableView(self._robot_model)
        self._robot_view.set_field(fields)

        # ========== 布局 ==========

        main_layout = QHBoxLayout(self)
        right_layout = QVBoxLayout()
        right_top_layout = FlowLayout()
        right_bottom_layout = QHBoxLayout()
        right_layout.addLayout(right_top_layout)
        right_layout.addLayout(right_bottom_layout)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._robot_view)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)

        from pprint import pprint

        self._robot_view.sClicked.connect(lambda x, y: pprint(y, depth=1))  # [TODO]

    # ========== 数据解析 ==========

    def set_rom_data(self, data: dict) -> None:
        """装入 ROM 的机体数据

        Args:
            data: Rom().parse_robots() 返回的 dict，
                  包含 "robots" 列表
        """
        self._rom_data = data
        robots = data.get("robots", [])
        self._robot_view.set_data(robots["robots"])

    def translateUI(self):
        """刷新界面翻译"""
        self._robot_view.set_title(
            {
                self.tr("robot name"): lambda x: x,
                self.tr("hit points"): lambda x: x,
                self.tr("energy"): lambda x: x,
                self.tr("movement"): lambda x: x,
                self.tr("mobility"): lambda x: x,
                self.tr("armor"): lambda x: x,
                self.tr("limit"): lambda x: x,
            }
        )

    def resetUI(self):
        """重置界面字体"""
        self._robot_view.resetUI()
