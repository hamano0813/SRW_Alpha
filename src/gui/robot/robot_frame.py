"""
机体编辑框架模块

提供机体数据的表格展示和编辑界面，配合 ROBOT.RAF 解析模块使用。
包含机体主列表和武器子列表的联动显示。

两层布局：SmoothScrollArea（遮罩）→ 容器 ProxyFrame（无布局，绝对定位）
- 下层：PanelFrame（固定缩进在 table_max_width 处，永远不会左右移动）
- 上层：UnitFrame 覆盖在上面，x=0，宽度 = min(视口宽, table_max_width)

常态：UnitFrame 直接填满整个视口宽度（遮挡右侧 Panel）
折叠：UnitFrame 宽度 = 第 0 列宽度，水平滚动条打开 → 露出右侧 Panel
窗口缩放时 Panel 位置不变，没有任何左右飞舞。

Classes:
    RobotFrame: 机体编辑框架（可平滑滚动）
"""

from PySide6.QtCore import QTimer, Qt
from qfluentwidgets import SmoothScrollArea

from gui.custom.models import BaseTableModel
from gui.custom.widgets.proxy_frame import ProxyFrame
from gui.robot.unit_frame import UnitFrame
from gui.robot.unit_panel import UnitPanel


class RobotFrame(SmoothScrollArea):
    """机体编辑框架 - 机体主列表 + 武器子列表联动（可平滑滚动）"""

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
        self.setWidgetResizable(False)
        self.enableTransparentBackground()

        self._rom_data: dict | None = None
        self._current_source_row: int = -1
        self._folded: bool = False

        # ========== 容器 ==========
        # 无布局，子控件通过绝对定位（setGeometry）手动放置。
        # 下层 Panel 固定缩进在 table_max_width，上层 Table 覆盖在左侧。

        self._container = ProxyFrame()
        self._container.resize(800, 32)  # 初始尺寸，第一次 resizeEvent 会修正

        # ========== 上层：机体主表（覆盖在左侧） ==========

        self._unit_frame = UnitFrame(self._container)
        self._unit_frame.set_field(fields)

        # ========== 下层：右侧面板（固定位置） ==========

        self._robot_panel = UnitPanel(self._container)
        self._robot_panel.set_model(self._unit_frame.robot_view.source_model())
        self._robot_panel.panelDataChanged.connect(self._on_panel_data_changed)

        # 确保 Panel 的 layout 已激活，sizeHint 准确
        self._robot_panel.layout().activate()

        # 默认隐藏右侧面板，仅在表格折叠后显示
        self._robot_panel.setVisible(False)

        self.setWidget(self._container)

        # 初始状态：水平滚动条关闭，Panel 在 table_max_width 右侧（被遮挡）
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._unit_frame.sClicked.connect(self._on_row_clicked)

        # ========== 名称编辑 → Rom 观察者通知 ==========

        self._unit_frame.robot_view.columnZeroEdited.connect(self._on_robot_name_edited)

        # ========== 列折叠 ↔ 面板联动 ==========

        self._unit_frame.robot_view.foldToggled.connect(self._on_fold_toggled)

    # ========== 全局定位 ==========

    def _update_layout(self):
        """根据当前状态重算所有子控件的位置和容器大小"""
        vp_w = self.viewport().width()
        vp_h = self.viewport().height()
        if vp_w <= 0 or vp_h <= 0:
            # 视口尚未就绪，尝试从窗口获取初始宽度作为 fallback
            win = self.window()
            if win and win.isVisible():
                vp_w = win.width() - 100
                vp_h = win.height() - 100
                if vp_w <= 0:
                    vp_w = 1000
                if vp_h <= 0:
                    vp_h = 600
            else:
                return  # 窗口尚未形成，等 resizeEvent

        # 表格最大宽度（所有列展开时的宽度）
        table_max = self._unit_frame.robot_view.get_content_width(False)

        # Panel 的自然宽度（始终保持不变）
        panel_w = self._robot_panel.sizeHint().width()

        # Table 宽度：折叠=仅第 0 列，常态=填满整个视口
        if self._folded:
            table_w = self._unit_frame.robot_view.get_content_width(True)
        else:
            table_w = vp_w

        # Panel 固定缩进位置（始终在 table_max 处，从不移动）
        panel_x = table_max

        # 设定几何
        self._unit_frame.setGeometry(0, 0, table_w, vp_h)
        self._robot_panel.setGeometry(panel_x, 0, panel_w, vp_h)

        # 容器总宽：展开态只需填满视口（Panel 在视口右侧被遮挡），
        # 折叠态需容纳 Table + Panel 以便滚动条生效
        if self._folded:
            total_w = max(vp_w, table_max + panel_w)
        else:
            total_w = vp_w
        self._container.resize(total_w, vp_h)

    def resizeEvent(self, event):
        """窗口缩放后刷新布局（延后一帧确保 viewport 已更新）"""
        super().resizeEvent(event)
        QTimer.singleShot(0, self._update_layout)

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

    # ========== 名称编辑通知 ==========

    def _on_robot_name_edited(self) -> None:
        """机体名称列编辑后，通知 Rom 重建 robots 索引并推送观察者"""
        rom = self.window().rom
        rom.notify("robots")

    # ========== 折叠联动 ==========

    def _on_fold_toggled(self, folded: bool, freed_width: int) -> None:
        """列折叠时切换格局

        折叠：Table 缩窄 → 露出下层 Panel → 打开水平滚动条
        展开：Table 撑满视口 → 遮住 Panel → 关闭滚动条并归零滚动位置

        Args:
            folded:       True=列已折叠，False=列已展开
            freed_width:  折叠释放的像素宽度（此方案中不使用）
        """
        self._folded = folded
        self._robot_panel.setVisible(folded)
        if folded:
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        else:
            self.horizontalScrollBar().setValue(0)
            self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._update_layout()

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

        # 数据加载后重新定位
        self._update_layout()

    # ========== 主题与翻译（委托给容器 ProxyFrame 自动传播） ==========

    def resetUI(self):
        """刷新所有子控件并更新布局"""
        self._container.resetUI()
        self._update_layout()

    def translateUI(self):
        """刷新所有子控件翻译并更新布局"""
        self._container.translateUI()
        # 翻译可能导致列宽变化，重新计算定位
        self._update_layout()
