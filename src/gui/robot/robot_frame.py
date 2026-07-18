"""
机体编辑框架模块

提供机体数据的表格展示和编辑界面，配合 ROBOT.RAF 解析模块使用。
包含机体主列表和武器子列表的联动显示。

Classes:
    RobotFrame: 机体编辑框架
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout

from gui.custom.proxy_frame import ProxyFrame
from gui.robot.unit_panel import UnitPanel
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
        self._current_source_row: int = -1

        # ========== 机体主表 ==========

        self._unit_frame = UnitFrame()
        self._unit_frame.set_field(fields)

        # ========== 右侧面板 ==========

        self._robot_panel = UnitPanel(self)
        self._robot_panel.panelDataChanged.connect(self._on_panel_data_changed)

        # ========== 布局 ==========

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._unit_frame)
        main_layout.addWidget(self._robot_panel)

        self._unit_frame.sClicked.connect(self._on_row_clicked)

        # ========== 列折叠 ↔ 面板联动 ==========

        self._unit_frame.robot_view.foldToggled.connect(self._on_fold_toggled)

    # ========== 行点击 ==========

    def _on_row_clicked(self, row: int, data: dict) -> None:
        """行点击时传递数据到右侧面板

        Args:
            row:  视图行号（转为源行号存储，供 model dataChanged 使用）
            data: 该行的数据字典
        """
        proxy = self._unit_frame.robot_view.proxy_model()
        self._current_source_row = proxy.mapToSource(proxy.index(row, 0)).row()
        self._robot_panel.set_row_data(data)

    # ========== 面板编辑回写 ==========

    def _on_panel_data_changed(self, field: str) -> None:
        """面板编辑器修改数据后通知 model 刷新对应单元格

        Args:
            field: 被修改的字段名
        """
        model = self._unit_frame.robot_view.source_model()
        for col, header in enumerate(model._headers):
            if model._fields.get_field(header) == field:
                idx = model.index(self._current_source_row, col)
                model.dataChanged.emit(idx, idx, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])
                break

    # ========== 折叠联动 ==========

    def _on_fold_toggled(self, folded: bool, freed_width: int) -> None:
        """列折叠时同步展开/收起右侧面板

        Args:
            folded:       True=列已折叠（展开面板），False=列已展开（收起面板）
            freed_width:  折叠释放的像素宽度（仅 folded=True 时有意义）
        """
        if folded:
            self._robot_panel.open_panel(freed_width)
        else:
            self._robot_panel.close_panel()

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

        # 默认选中第一行
        if robots["robots"]:
            self._unit_frame.robot_view.selectRow(0)
            self._on_row_clicked(0, robots["robots"][0])
