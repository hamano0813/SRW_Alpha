"""
机体编辑框架模块

提供机体数据的表格展示和编辑界面，配合 ROBOT.RAF 解析模块使用。
包含机体主列表和武器子列表的联动显示。

常态：机体表格填满视口，右侧面板隐藏。
折叠：表格缩至首列宽度，右侧面板露出，水平滚动条出现。

右侧面板内部分左右两列：
  左列：变形·合体 / 地形适性 / BGM 卡片 + 武器表格
  右列：能力列表 / 系列卡片 + 武器编辑卡片

Classes:
    UnitFrame: 机体编辑框架（可平滑滚动）
"""

from PySide6.QtCore import QEasingCurve, Qt, QTimer, QVariantAnimation
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QSizePolicy,
    QSpacerItem,
    QVBoxLayout,
)
from qfluentwidgets import SmoothScrollArea

from gui.custom import EnumData, JP_FONT
from gui.widget import (
    BaseTableModel,
    FixedTableView,
    MappingSpinDelegate,
    NumberSpinDelegate,
    ProxyFrame,
    SingleLineDelegate,
)
from gui.interface.unit.cards import (
    AbilitiesCard,
    BgmCard,
    SeriesCard,
    TerrainCard,
    TransformCard,
    WeaponAdaptCard,
    WeaponAttrCard,
    WeaponMapCard,
)
from gui.interface.unit.weapon_list import WeaponListCard


class UnitFrame(SmoothScrollArea):
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
        self.setObjectName("UnitFrame")
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

        self._unit_view = self._build_unit_table(fields)
        layout.addWidget(self._unit_view, 1)

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
        self._transform_card.set_model(self._unit_view.source_model())
        self._transform_card.panelDataChanged.connect(self._on_panel_data_changed)
        top_row_layout.addWidget(self._transform_card)

        self._terrain_card = TerrainCard(top_row)
        self._terrain_card.set_model(self._unit_view.source_model())
        self._terrain_card.panelDataChanged.connect(self._on_panel_data_changed)
        top_row_layout.addWidget(self._terrain_card)

        left_cards_layout.addWidget(top_row)

        self._bgm_card = BgmCard(left_cards)
        self._bgm_card.set_model(self._unit_view.source_model())
        self._bgm_card.panelDataChanged.connect(self._on_panel_data_changed)
        left_cards_layout.addWidget(self._bgm_card)

        right_grid.addWidget(left_cards, 0, 0)

        # (0,1) 右列卡片：能力列表 + 系列（横排）
        right_cards = ProxyFrame(self._right_panel)
        right_cards_layout = QHBoxLayout(right_cards)
        right_cards_layout.setContentsMargins(0, 0, 0, 0)
        right_cards_layout.setSpacing(8)

        self._abilities_card = AbilitiesCard(right_cards)
        self._abilities_card.set_model(self._unit_view.source_model())
        self._abilities_card.panelDataChanged.connect(self._on_panel_data_changed)
        right_cards_layout.addWidget(self._abilities_card)

        self._series_card = SeriesCard(right_cards)
        self._series_card.set_model(self._unit_view.source_model())
        self._series_card.panelDataChanged.connect(self._on_panel_data_changed)
        right_cards_layout.addWidget(self._series_card)

        right_grid.addWidget(right_cards, 0, 1)

        # (1,0) 左下：武器列表卡片
        self._weapon_card = WeaponListCard(self._right_panel)
        self._weapon_card.set_field(fields)
        self._weapon_card.table.sClicked.connect(self._on_weapon_row_clicked)
        right_grid.addWidget(self._weapon_card, 1, 0, 3, 1)

        # (1,1) 右下：武器编辑卡片
        #   上排：武器属性卡片
        #   下排：地图武器 + 地形适应（平行）
        weapon_cards = ProxyFrame(self._right_panel)
        weapon_layout = QVBoxLayout(weapon_cards)
        weapon_layout.setContentsMargins(0, 0, 0, 0)
        weapon_layout.setSpacing(8)

        self._weapon_attr_card = WeaponAttrCard(weapon_cards)
        self._weapon_attr_card.panelDataChanged.connect(self._on_panel_data_changed)
        weapon_layout.addWidget(self._weapon_attr_card)

        weapon_bottom = QHBoxLayout()
        weapon_bottom.setSpacing(8)

        self._weapon_map_card = WeaponMapCard(weapon_cards)
        self._weapon_map_card.panelDataChanged.connect(self._on_panel_data_changed)
        weapon_bottom.addWidget(self._weapon_map_card)

        self._weapon_adapt_card = WeaponAdaptCard(weapon_cards)
        self._weapon_adapt_card.panelDataChanged.connect(self._on_panel_data_changed)
        weapon_bottom.addWidget(self._weapon_adapt_card)

        weapon_layout.addLayout(weapon_bottom)

        right_grid.addWidget(weapon_cards, 1, 1)

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

        # ========== 卡片列表（统一 translateUI / resetUI） ==========

        self._cards = [
            self._transform_card,
            self._terrain_card,
            self._bgm_card,
            self._abilities_card,
            self._series_card,
            self._weapon_attr_card,
            self._weapon_map_card,
            self._weapon_adapt_card,
        ]

        self._unit_view.sClicked.connect(self._on_row_clicked)
        self._unit_view.columnZeroEdited.connect(self._on_robot_name_edited)
        self._unit_view.foldToggled.connect(self._on_fold_toggled)

        # 初始化列标题（后续 translateUI 会重新刷新）
        self._translate_unit_headers()

    # ========== 表格构建 ==========

    def _build_unit_table(self, fields) -> FixedTableView:
        """创建机体表格并配置委托、列宽、字体"""
        view = FixedTableView()
        view.set_field(fields)

        _model = view.source_model()
        _model.set_font({0: JP_FONT})
        _model.set_alignments({
            1: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            2: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            3: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            4: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            5: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            6: Qt.AlignmentFlag.AlignCenter,
            7: Qt.AlignmentFlag.AlignCenter,
            8: Qt.AlignmentFlag.AlignCenter,
            9: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            10: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        })

        self._name_delegate = SingleLineDelegate(font=JP_FONT, parent=view)
        view.setItemDelegateForColumn(0, self._name_delegate)

        self._hp_delegate = NumberSpinDelegate(value_range=(0, 65535), show_buttons=False, parent=view)
        view.setItemDelegateForColumn(1, self._hp_delegate)
        self._en_delegate = NumberSpinDelegate(value_range=(50, 400), show_buttons=False, parent=view)
        view.setItemDelegateForColumn(2, self._en_delegate)
        self._mobility_delegate = NumberSpinDelegate(value_range=(40, 200), show_buttons=False, parent=view)
        view.setItemDelegateForColumn(3, self._mobility_delegate)
        self._armor_delegate = NumberSpinDelegate(value_range=(100, 4000), show_buttons=False, parent=view)
        view.setItemDelegateForColumn(4, self._armor_delegate)
        self._limit_delegate = NumberSpinDelegate(value_range=(200, 600), show_buttons=False, parent=view)
        view.setItemDelegateForColumn(5, self._limit_delegate)

        self._slot_delegate = NumberSpinDelegate(value_range=(1, 4), show_buttons=True, parent=view)
        view.setItemDelegateForColumn(7, self._slot_delegate)
        self._move_delegate = NumberSpinDelegate(value_range=(3, 9), show_buttons=True, parent=view)
        view.setItemDelegateForColumn(8, self._move_delegate)

        _enum = EnumData()
        self._size_delegate = MappingSpinDelegate(mapping=_enum.ROBOT["SIZE"], parent=view)
        view.setItemDelegateForColumn(6, self._size_delegate)

        self._rep_delegate = NumberSpinDelegate(value_range=(0, 65535), show_buttons=False, parent=view)
        view.setItemDelegateForColumn(9, self._rep_delegate)
        self._cost_delegate = NumberSpinDelegate(value_range=(0, 65535), show_buttons=False, parent=view)
        view.setItemDelegateForColumn(10, self._cost_delegate)

        view.set_column_width([210, 120] + [110] * 7 + [115] * 2)
        view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        view.verticalHeader().setFixedWidth(45)

        return view

    def _translate_unit_headers(self) -> None:
        """刷新机体表格列标题与格式化函数"""
        self._unit_view.set_title({
            self.tr("Robot name"): [self._name_delegate.format_display, self._name_delegate.parse_display],
            self.tr("Hit points"): [self._hp_delegate.format_display, self._hp_delegate.parse_display],
            self.tr("Energy"): [self._en_delegate.format_display, self._en_delegate.parse_display],
            self.tr("Mobility"): [self._mobility_delegate.format_display, self._mobility_delegate.parse_display],
            self.tr("Armor"): [self._armor_delegate.format_display, self._armor_delegate.parse_display],
            self.tr("Limit"): [self._limit_delegate.format_display, self._limit_delegate.parse_display],
            self.tr("Size"): [self._size_delegate.format_display, self._size_delegate.parse_display],
            self.tr("Parts slot"): [self._slot_delegate.format_display, self._slot_delegate.parse_display],
            self.tr("Movement"): [self._move_delegate.format_display, self._move_delegate.parse_display],
            self.tr("Repair cost"): [self._rep_delegate.format_display, self._rep_delegate.parse_display],
            self.tr("Cost"): [self._cost_delegate.format_display, self._cost_delegate.parse_display],
        })
        if self._unit_view.column_widths:
            self._unit_view.set_column_width(self._unit_view.column_widths)

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
            self._weapon_card.set_data(weapons)
            w_model = self._weapon_card.source_model()
            for card in [self._weapon_attr_card, self._weapon_map_card, self._weapon_adapt_card]:
                card.set_model(w_model)
            if w_model.rowCount() > 0:
                self._weapon_card.select_source_row(0)
                self._on_weapon_row_clicked(0, w_model)

    # ========== 武器行点击 ==========

    def _on_weapon_row_clicked(self, source_row: int, model: BaseTableModel) -> None:
        """武器行单击时刷新武器编辑卡片"""
        self._weapon_attr_card.set_row(source_row)
        self._weapon_map_card.set_row(source_row)
        self._weapon_adapt_card.set_row(source_row)

    # ========== 面板编辑回写 ==========

    def _on_panel_data_changed(self, field: str) -> None:
        """面板编辑器修改数据后通知 model 刷新对应单元格"""
        model = self._unit_view.source_model()
        for col, header in enumerate(model.headers):
            mapped = model.fields.get_field(header)
            if mapped == field:
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
        start_w = self._unit_view.width()

        if folded:
            self._right_panel.setVisible(True)
            end_w = self._unit_view.get_content_width(True)
            self._kill_anim()
            self._anim = QVariantAnimation(self)
            self._anim.valueChanged.connect(lambda v: self._unit_view.setFixedWidth(v))
            self._anim.finished.connect(lambda: self._on_fold_anim_done(end_w))
            self._anim.setDuration(200)
            self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
            self._anim.setStartValue(start_w)
            self._anim.setEndValue(end_w)
            self._anim.start(QVariantAnimation.DeletionPolicy.KeepWhenStopped)
        else:
            self._right_panel.setVisible(False)
            end_w = self.viewport().width()
            self._kill_anim()
            self._anim = QVariantAnimation(self)
            self._anim.valueChanged.connect(lambda v: self._unit_view.setFixedWidth(v))
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
                pass
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
        self._unit_view.setFixedWidth(target_w)

    def _on_unfold_anim_done(self) -> None:
        """展开动画完成后的收尾工作"""
        anim = getattr(self, '_anim', None)
        if anim is not None:
            try:
                anim.deleteLater()
            except RuntimeError:
                pass
        self._anim = None
        self._unit_view.setMinimumWidth(0)
        self._unit_view.setMaximumWidth(16777215)
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
        self._unit_view.set_data(robots["robots"])

        # 默认选中第一行
        model = self._unit_view.source_model()
        if model.rowCount() > 0:
            self._unit_view.selectRow(0)
            self._on_row_clicked(0, model)

        self._update_layout()

    # ========== 主题与翻译 ==========

    def resetUI(self):
        """刷新所有子控件并更新布局"""
        self._container.resetUI()
        for card in self._cards:
            card.resetUI()
        self._weapon_card.resetUI()
        self._update_layout()

    def translateUI(self):
        """刷新所有子控件翻译并更新布局"""
        self._container.translateUI()
        self._translate_unit_headers()
        for card in self._cards:
            card.translateUI()
        self._weapon_card.translateUI()
        self._update_layout()
