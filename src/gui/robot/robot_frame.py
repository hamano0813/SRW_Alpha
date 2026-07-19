"""
机体编辑框架模块

提供机体数据的表格展示和编辑界面，配合 ROBOT.RAF 解析模块使用。
包含机体主列表和武器子列表的联动显示。

Classes:
    RobotFrame: 机体编辑框架
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout

from gui.custom.models import BaseTableModel
from gui.custom.widgets.proxy_frame import ProxyFrame
from gui.robot.unit_frame import UnitFrame
from gui.robot.unit_panel import UnitPanel


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
        self._robot_panel.set_model(self._unit_frame.robot_view.source_model())
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

    def _on_row_clicked(self, source_row: int, model: BaseTableModel) -> None:
        """行点击时通知面板切换行

        model 为 QObject 实例，跨信号不复制，仅用于
        set_rom_data 首次调用时的初始化路径。

        Args:
            source_row: 源模型行号（已在 _single_click 中完成代理映射）
            model:      BaseTableModel 实例
        """
        self._current_source_row = source_row
        self._robot_panel.set_row(source_row)

    # ========== 面板编辑回写 ==========

    def _on_panel_data_changed(self, field: str) -> None:
        """面板编辑器修改数据后通知 model 刷新对应单元格"""
        model = self._unit_frame.robot_view.source_model()
        for col, header in enumerate(model.headers):
            if model.fields.get_field(header) == field:
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
        model = self._unit_frame.robot_view.source_model()
        if model.rowCount() > 0:
            self._unit_frame.robot_view.selectRow(0)
            self._on_row_clicked(0, model)
