"""
驾驶员编辑框架模块

提供驾驶员数据的表格展示和编辑界面，配合 PILOT.BIN 解析模块使用。
左侧为驾驶员列表表格，右侧为各属性编辑卡片。

Classes:
    PilotFrame: 驾驶员编辑框架（可平滑滚动）
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QHBoxLayout, QHeaderView, QVBoxLayout
from qfluentwidgets import SmoothScrollArea

from gui.custom import JP_FONT
from gui.widget import (
    BaseTableModel,
    FixedTableView,
    NumberSpinDelegate,
    ProxyFrame,
    SingleLineDelegate,
    SpiritsEditor,
)
from gui.interface.pilot.cards import (
    PilotDetailCard,
    SeriesCard,
    SpecialSkillsCard,
    TerrainCard,
    UpgradedSkillsCard,
)


class PilotFrame(SmoothScrollArea):
    """驾驶员编辑框架 - 驾驶员表格 + 编辑卡片联动（可平滑滚动）"""

    def __init__(
        self,
        fields,
        parent=None,
    ):
        """初始化驾驶员编辑框架

        Args:
            fields: FieldMapping 字段映射实例
            parent: 父 QWidget
        """
        super().__init__(parent)
        self.setObjectName("PilotFrame")
        self.setWidgetResizable(False)
        self.enableTransparentBackground()

        self._rom_data: dict | None = None
        self._current_source_row: int = -1

        # ========== 容器（水平布局：驾驶员表格 | 右侧卡片） ==========

        self._container = ProxyFrame()
        self._container.resize(800, 32)
        self.setWidget(self._container)

        layout = QHBoxLayout(self._container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ===== 左侧：驾驶员表格 =====

        self._pilot_view = self._build_pilot_table(fields)
        layout.addWidget(self._pilot_view, 1)

        # ===== 右侧：编辑卡片 =====

        self._right_panel = ProxyFrame(self._container)
        cards_layout = QVBoxLayout(self._right_panel)
        cards_layout.setSpacing(8)
        cards_layout.setContentsMargins(8, 8, 8, 8)

        # 模型在 FixedTableView 构造时已创建，所有卡片共享
        _model = self._pilot_view.source_model()

        self._detail_card = PilotDetailCard(self._right_panel)
        self._detail_card.set_model(_model)
        cards_layout.addWidget(self._detail_card)

        self._spirits_card = SpiritsEditor(self._right_panel)
        self._spirits_card.setTitle(self.tr("Spirits"))
        self._spirits_card.set_model(_model)
        self._spirits_card.panelDataChanged.connect(self._on_panel_data_changed)
        cards_layout.addWidget(self._spirits_card)

        self._terrain_card = TerrainCard(self._right_panel)
        self._terrain_card.set_model(_model)
        self._terrain_card.panelDataChanged.connect(self._on_panel_data_changed)
        cards_layout.addWidget(self._terrain_card)

        self._series_card = SeriesCard(self._right_panel)
        self._series_card.set_model(_model)
        self._series_card.panelDataChanged.connect(self._on_panel_data_changed)
        cards_layout.addWidget(self._series_card)

        self._skills_card = SpecialSkillsCard(self._right_panel)
        self._skills_card.set_model(_model)
        cards_layout.addWidget(self._skills_card)

        self._upgraded_card = UpgradedSkillsCard(self._right_panel)
        self._upgraded_card.set_model(_model)
        cards_layout.addWidget(self._upgraded_card)

        cards_layout.addStretch()

        layout.addWidget(self._right_panel)

        # 默认隐藏右侧面板，首次点击行后显示
        self._right_panel.setVisible(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # ========== 卡片列表（统一 translateUI / resetUI） ==========

        self._cards = [
            self._detail_card,
            self._spirits_card,
            self._terrain_card,
            self._series_card,
            self._skills_card,
            self._upgraded_card,
        ]

        self._pilot_view.sClicked.connect(self._on_row_clicked)
        self._pilot_view.columnZeroEdited.connect(self._on_pilot_name_edited)

        # 初始化列标题（后续 translateUI 会重新刷新）
        self._translate_pilot_headers()

    # ========== 表格构建 ==========

    def _build_pilot_table(self, fields) -> FixedTableView:
        """创建驾驶员表格并配置委托、列宽、字体"""
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
            6: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        })

        self._name_delegate = SingleLineDelegate(font=JP_FONT, parent=view)
        view.setItemDelegateForColumn(0, self._name_delegate)

        self._cqb_delegate = NumberSpinDelegate(value_range=(0, 999), show_buttons=False, parent=view)
        view.setItemDelegateForColumn(1, self._cqb_delegate)
        self._rng_delegate = NumberSpinDelegate(value_range=(0, 999), show_buttons=False, parent=view)
        view.setItemDelegateForColumn(2, self._rng_delegate)
        self._evd_delegate = NumberSpinDelegate(value_range=(0, 999), show_buttons=False, parent=view)
        view.setItemDelegateForColumn(3, self._evd_delegate)
        self._hit_delegate = NumberSpinDelegate(value_range=(0, 999), show_buttons=False, parent=view)
        view.setItemDelegateForColumn(4, self._hit_delegate)
        self._rxn_delegate = NumberSpinDelegate(value_range=(0, 999), show_buttons=False, parent=view)
        view.setItemDelegateForColumn(5, self._rxn_delegate)
        self._skl_delegate = NumberSpinDelegate(value_range=(0, 999), show_buttons=False, parent=view)
        view.setItemDelegateForColumn(6, self._skl_delegate)

        view.set_column_width([125] + [90] * 6)
        view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        view.verticalHeader().setFixedWidth(45)
        view.setShowGrid(True)
        view._corner_button.setVisible(False)

        return view

    def _translate_pilot_headers(self) -> None:
        """刷新驾驶员表格列标题与格式化函数"""
        self._pilot_view.set_title({
            self.tr("Nickname"): [self._name_delegate.format_display, self._name_delegate.parse_display],
            self.tr("Combat"): [self._cqb_delegate.format_display, self._cqb_delegate.parse_display],
            self.tr("Ranged"): [self._rng_delegate.format_display, self._rng_delegate.parse_display],
            self.tr("Evasion"): [self._evd_delegate.format_display, self._evd_delegate.parse_display],
            self.tr("Accuracy"): [self._hit_delegate.format_display, self._hit_delegate.parse_display],
            self.tr("Reaction"): [self._rxn_delegate.format_display, self._rxn_delegate.parse_display],
            self.tr("Skill"): [self._skl_delegate.format_display, self._skl_delegate.parse_display],
        })
        if self._pilot_view.column_widths:
            self._pilot_view.set_column_width(self._pilot_view.column_widths)

    # ========== 全局定位 ==========

    def _update_layout(self):
        """根据面板可见性调整容器尺寸"""
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

        self._container.resize(vp_w, vp_h)

    def resizeEvent(self, event):
        """窗口缩放后刷新布局"""
        super().resizeEvent(event)
        QTimer.singleShot(0, self._update_layout)

    # ========== 行点击 ==========

    def _on_row_clicked(self, source_row: int, model: BaseTableModel) -> None:
        """行点击时显示面板并切换行数据

        Args:
            source_row: 源模型行号
            model:      BaseTableModel 实例
        """
        self._current_source_row = source_row

        # 首次点击时显示右侧面板
        if not self._right_panel.isVisible():
            self._right_panel.setVisible(True)
            QTimer.singleShot(0, self._update_layout)

        for card in self._cards:
            card.set_row(source_row)

    # ========== 面板编辑回写 ==========

    def _on_panel_data_changed(self, field: str) -> None:
        """面板编辑器修改数据后通知 model 刷新对应单元格"""
        model = self._pilot_view.source_model()
        for col, header in enumerate(model.headers):
            mapped = model.fields.get_field(header)
            if mapped == field:
                idx = model.index(self._current_source_row, col)
                model.dataChanged.emit(idx, idx, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])
                break

    # ========== 名称编辑通知 ==========

    def _on_pilot_name_edited(self) -> None:
        """驾驶员名称列编辑后，通知 Rom 重建 pilots 索引并推送观察者"""
        rom = self.window().rom
        rom.notify("pilots")

    # ========== 数据解析 ==========

    def set_rom_data(self, data: dict) -> None:
        """装入 ROM 的驾驶员数据

        Args:
            data: Rom().parse_pilots() 返回的 dict，
                  包含 "pilots" 列表
        """
        self._rom_data = data
        pilots = data.get("pilots", {})
        self._pilot_view.set_data(pilots.get("pilots", []))

        # 默认选中第一行
        model = self._pilot_view.source_model()
        if model.rowCount() > 0:
            self._pilot_view.selectRow(0)
            self._on_row_clicked(0, model)

        self._update_layout()

    # ========== 主题与翻译 ==========

    def resetUI(self):
        """刷新所有子控件并更新布局"""
        self._container.resetUI()
        for card in self._cards:
            card.resetUI()
        self._update_layout()

    def translateUI(self):
        """刷新所有子控件翻译并更新布局"""
        self._container.translateUI()
        self._translate_pilot_headers()
        for card in self._cards:
            card.translateUI()
        self._update_layout()
