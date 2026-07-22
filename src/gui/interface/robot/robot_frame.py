"""
机体编辑框架模块

提供机体数据的表格展示和编辑界面，配合 ROBOT.RAF 解析模块使用。
包含机体主列表和武器子列表的联动显示。

常态：UnitFrame 填满视口，右侧面板隐藏。
折叠：UnitFrame 固定在首列宽度，右侧面板露出，水平滚动条出现。

右侧面板内部分左右两列：
  左列：变形·合体 / 地形适性 / BGM 卡片 + 武器表格
  右列：能力列表 / 系列卡片 + 武器编辑面板

Classes:
    RobotFrame: 机体编辑框架（可平滑滚动）
"""

from PySide6.QtCore import QEasingCurve, Qt, QTimer, QVariantAnimation
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)
from qfluentwidgets import SmoothScrollArea

from gui.widget import BaseTableModel, ProxyFrame
from gui.interface.robot.unit_frame import UnitFrame
from gui.interface.robot.unit_panel import (
    AbilitiesCard,
    BgmCard,
    SeriesCard,
    TerrainCard,
    TransformCard,
)
from gui.interface.robot.weapon_frame import WeaponListCard, WeaponView
from gui.interface.robot.weapon_panel import WeaponPanel


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

        # ========== 容器（水平布局：机体表格 | 右侧面板组） ==========

        self._container = ProxyFrame()
        self._container.resize(800, 32)
        self.setWidget(self._container)

        layout = QHBoxLayout(self._container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ===== 左侧：机体主表 =====

        self._unit_frame = UnitFrame(self._container)
        self._unit_frame.set_field(fields)
        layout.addWidget(self._unit_frame, 1)

        # ===== 右侧面板组 =====

        self._right_panel = ProxyFrame(self._container)
        right_grid = QGridLayout(self._right_panel)
        right_grid.setContentsMargins(0, 0, 0, 0)
        right_grid.setHorizontalSpacing(8)
        right_grid.setVerticalSpacing(24)

        # (0,0) 左列卡片：变形 + 地形（横排）+ BGM（下）
        left_cards = ProxyFrame(self._right_panel)
        left_cards_layout = QVBoxLayout(left_cards)
        left_cards_layout.setContentsMargins(0, 0, 0, 0)
        left_cards_layout.setSpacing(8)

        top_row = ProxyFrame(left_cards)
        top_row_layout = QHBoxLayout(top_row)
        top_row_layout.setContentsMargins(0, 0, 0, 0)
        top_row_layout.setSpacing(8)

        self._transform_card = TransformCard(top_row)
        self._transform_card.set_model(self._unit_frame.robot_view.source_model())
        self._transform_card.panelDataChanged.connect(self._on_panel_data_changed)
        top_row_layout.addWidget(self._transform_card)

        self._terrain_card = TerrainCard(top_row)
        self._terrain_card.set_model(self._unit_frame.robot_view.source_model())
        self._terrain_card.panelDataChanged.connect(self._on_panel_data_changed)
        top_row_layout.addWidget(self._terrain_card)

        left_cards_layout.addWidget(top_row)

        self._bgm_card = BgmCard(left_cards)
        self._bgm_card.set_model(self._unit_frame.robot_view.source_model())
        self._bgm_card.panelDataChanged.connect(self._on_panel_data_changed)
        left_cards_layout.addWidget(self._bgm_card)

        right_grid.addWidget(left_cards, 0, 0)

        # (0,1) 右列卡片：能力列表 + 系列（横排）
        right_cards = ProxyFrame(self._right_panel)
        right_cards_layout = QHBoxLayout(right_cards)
        right_cards_layout.setContentsMargins(0, 0, 0, 0)
        right_cards_layout.setSpacing(8)

        self._abilities_card = AbilitiesCard(right_cards)
        self._abilities_card.set_model(self._unit_frame.robot_view.source_model())
        self._abilities_card.panelDataChanged.connect(self._on_panel_data_changed)
        right_cards_layout.addWidget(self._abilities_card)

        self._series_card = SeriesCard(right_cards)
        self._series_card.set_model(self._unit_frame.robot_view.source_model())
        self._series_card.panelDataChanged.connect(self._on_panel_data_changed)
        right_cards_layout.addWidget(self._series_card)

        right_grid.addWidget(right_cards, 0, 1)

        # (1,0) 左下：武器表格（外套卡片）
        self._weapon_card = WeaponListCard(self._right_panel)
        self._weapon_view = WeaponView(self._weapon_card)
        self._weapon_view.set_field(fields)
        self._weapon_view.sClicked.connect(self._on_weapon_row_clicked)
        self._weapon_card.viewLayout.addWidget(self._weapon_view)
        right_grid.addWidget(self._weapon_card, 1, 0, 3, 1)

        # (1,1) 右下：武器编辑面板
        self._weapon_panel = WeaponPanel(self._right_panel)
        self._weapon_panel.panelDataChanged.connect(self._on_panel_data_changed)
        right_grid.addWidget(self._weapon_panel, 1, 1)

        # 右下角伸缩 spacer，把内容撑到左上角
        right_grid.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding), 2, 2)
        right_grid.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding), 3, 2)
        right_grid.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding), 4, 3)
        right_grid.addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding), 5, 4)

        layout.addWidget(self._right_panel)
        layout.addStretch()

        # 默认隐藏右侧面板组，仅在表格折叠后显示
        self._right_panel.setVisible(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._unit_frame.sClicked.connect(self._on_row_clicked)
        self._unit_frame.robot_view.columnZeroEdited.connect(self._on_robot_name_edited)
        self._unit_frame.robot_view.foldToggled.connect(self._on_fold_toggled)

    # ========== 全局定位 ==========

    def _update_layout(self):
        """根据折叠状态调整容器尺寸"""
        vp_w = self.viewport().width()
        vp_h = self.viewport().height()
        if vp_w <= 0 or vp_h <= 0:
            win = self.window()
            if win and win.isVisible():
                vp_w = win.width() - 100
                vp_h = win.height() - 100
                if vp_w <= 0:
                    vp_w = 1000
                if vp_h <= 0:
                    vp_h = 600
            else:
                return

        if self._folded:
            total_w = max(vp_w, self._container.layout().minimumSize().width())
        else:
            total_w = vp_w
        self._container.resize(total_w, vp_h)

    def resizeEvent(self, event):
        """窗口缩放后刷新布局"""
        super().resizeEvent(event)
        QTimer.singleShot(0, self._update_layout)

    # ========== 行点击 ==========

    def _on_row_clicked(self, source_row: int, model: BaseTableModel) -> None:
        """行点击时通知卡片切换行

        Args:
            source_row: 源模型行号
            model:      BaseTableModel 实例
        """
        self._current_source_row = source_row
        self._transform_card.set_row(source_row)
        self._terrain_card.set_row(source_row)
        self._bgm_card.set_row(source_row)
        self._abilities_card.set_row(source_row)
        self._series_card.set_row(source_row)

        # 同步武器数据
        if self._rom_data is not None:
            weapons = self._rom_data["robots"]["robots"][source_row]["weapons"]
            self._weapon_view.set_data(weapons)
            w_model = self._weapon_view.source_model()
            self._weapon_panel.set_model(w_model)
            if w_model.rowCount() > 0:
                self._weapon_view.select_source_row(0)
                self._on_weapon_row_clicked(0, w_model)

    # ========== 武器行点击 ==========

    def _on_weapon_row_clicked(self, source_row: int, model: BaseTableModel) -> None:
        """武器行单击时刷新武器编辑面板"""
        self._weapon_panel.set_row(source_row)

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

    # ========== 折叠联动（带动画） ==========

    def _on_fold_toggled(self, folded: bool, freed_width: int) -> None:
        """列折叠时带动画切换格局

        折叠：Table 缩窄 → 露出右侧面板 → 打开水平滚动条
        展开：Table 撑满视口 → 遮住面板 → 关闭滚动条并归零滚动位置
        """
        self._folded = folded
        start_w = self._unit_frame.width()

        if folded:
            # 折叠：先显示面板，再缩窄表格
            self._right_panel.setVisible(True)
            end_w = self._unit_frame.robot_view.get_content_width(True)
            self._kill_anim()
            self._anim = QVariantAnimation(self)
            self._anim.valueChanged.connect(lambda v: self._unit_frame.setFixedWidth(v))
            self._anim.finished.connect(lambda: self._on_fold_anim_done(end_w))
            self._anim.setDuration(200)
            self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._anim.setStartValue(start_w)
            self._anim.setEndValue(end_w)
            self._anim.start(QVariantAnimation.DeletionPolicy.KeepWhenStopped)
        else:
            # 展开：先隐藏面板，再撑宽表格
            self._right_panel.setVisible(False)
            end_w = self.viewport().width()
            self._kill_anim()
            self._anim = QVariantAnimation(self)
            self._anim.valueChanged.connect(lambda v: self._unit_frame.setFixedWidth(v))
            self._anim.finished.connect(lambda: self._on_unfold_anim_done())
            self._anim.setDuration(200)
            self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._anim.setStartValue(start_w)
            self._anim.setEndValue(end_w)
            self._anim.start(QVariantAnimation.DeletionPolicy.KeepWhenStopped)

    def _kill_anim(self) -> None:
        """停止并清理进行中的动画"""
        anim = getattr(self, '_anim', None)
        if anim is not None:
            try:
                anim.stop()
            except RuntimeError:
                pass  # C++ 对象已销毁
            self._anim = None

    def _on_fold_anim_done(self, target_w: int) -> None:
        """折叠动画完成后的收尾工作"""
        anim = getattr(self, '_anim', None)
        if anim is not None:
            try:
                anim.deleteLater()
            except RuntimeError:
                pass
        self._anim = None
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._unit_frame.setFixedWidth(target_w)

    def _on_unfold_anim_done(self) -> None:
        """展开动画完成后的收尾工作"""
        anim = getattr(self, '_anim', None)
        if anim is not None:
            try:
                anim.deleteLater()
            except RuntimeError:
                pass
        self._anim = None
        self._unit_frame.setMinimumWidth(0)
        self._unit_frame.setMaximumWidth(16777215)
        self.horizontalScrollBar().setValue(0)
        self._update_layout()
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

        self._update_layout()

    # ========== 主题与翻译 ==========

    def resetUI(self):
        """刷新所有子控件并更新布局"""
        self._container.resetUI()
        self._weapon_panel.resetUI()
        self._weapon_view.resetUI()
        self._update_layout()

    def translateUI(self):
        """刷新所有子控件翻译并更新布局"""
        self._container.translateUI()
        self._weapon_view.translateUI()
        self._weapon_panel.translateUI()
        self._update_layout()
