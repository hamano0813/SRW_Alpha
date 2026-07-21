"""
武器编辑子框架 - 武器表格 + 右侧面板

包含 WeaponView（武器表格）和 3 张编辑卡片。
采用类似 RobotFrame 的折叠布局：
- 表格展开时占满整个宽度，面板隐藏
- 表格折叠（仅第 0 列）时面板出现在右侧

WeaponFrame 自身不管理外层高度，由父级（RobotFrame）通过 setGeometry 定位。

Classes:
    WeaponAttrCard:    武器属性卡片（含射程/命中/会心/需求）
    WeaponMapCard:     地图武器卡片
    WeaponAdaptCard:   地形适应卡片（空陆海宇）
    WeaponPanel:    右侧面板容器
    WeaponFrame:    武器编辑框架
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QSizePolicy, QVBoxLayout
from qfluentwidgets import BodyLabel, setFont

from gui.custom.enums import EnumData
from gui.custom.fonts import JP_FONT, JP_QFONT
from gui.custom.models import BaseTableModel
from gui.custom.widgets import BitComboBox, MappingComboBox, NumberCompSpin
from gui.custom.widgets.special import AmmoSpin, RangeComboBox
from gui.custom.widgets.card_header import CardHeader
from gui.custom.widgets.panel.mapping_compspin import MappingCompSpin
from gui.custom.widgets.proxy_frame import ProxyFrame

from .weapon_view import WeaponView


# =============================================================================
# 卡片占位 — 各卡片内容后续逐步填充
# =============================================================================


class WeaponAttrCard(CardHeader):
    """武器属性卡片 - 武器属性 + 其他参数"""

    def __init__(self, parent=None):
        """初始化武器属性卡片"""
        super().__init__(parent)
        self.setTitle(self.tr("Weapon Details"))

        # ========== 控件 ==========

        self._model = None
        self._row = -1
        self._attr_combo = BitComboBox("attr", values=EnumData().WEAPON["ATTRIBUTE"], sep=" / ", parent=self)
        self._attr_combo.setMinimumWidth(479)
        self._attr_combo.dataChanged.connect(self.panelDataChanged)

        self._rngs_label = BodyLabel(self.tr("Short rng"), self)
        self._rngs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._rngs_label.setMinimumWidth(70)
        self._rngs_spin = NumberCompSpin("rngs", value_range=(0, 3), parent=self)
        self._rngs_spin.setFixedWidth(70)
        self._rngs_spin.dataChanged.connect(self.panelDataChanged)

        self._rngl_label = BodyLabel(self.tr("Long rng"), self)
        self._rngl_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._rngl_label.setMinimumWidth(70)
        self._rngl_spin = NumberCompSpin("rngl", value_range=(0, 15), parent=self)
        self._rngl_spin.setFixedWidth(72)
        self._rngl_spin.dataChanged.connect(self.panelDataChanged)

        self._hit_label = BodyLabel(self.tr("Accuracy"), self)
        self._hit_label.setMinimumWidth(70)
        self._hit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._hit_spin = NumberCompSpin("hit", value_range=(-99, 99), show_sign=True, parent=self)
        self._hit_spin.setFixedWidth(65)
        self._hit_spin.dataChanged.connect(self.panelDataChanged)

        self._crt_label = BodyLabel(self.tr("Critical"), self)
        self._crt_label.setMinimumWidth(70)
        self._crt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._crt_spin = NumberCompSpin("crt", value_range=(-99, 99), show_sign=True, parent=self)
        self._crt_spin.setFixedWidth(65)
        self._crt_spin.dataChanged.connect(self.panelDataChanged)

        self._morale_label = BodyLabel(self.tr("Morale"), self)
        self._morale_label.setMinimumWidth(70)
        self._morale_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._morale_spin = NumberCompSpin("morale", value_range=(0, 150), parent=self)
        self._morale_spin.setFixedWidth(65)
        self._morale_spin.dataChanged.connect(self.panelDataChanged)

        self._newtype_label = BodyLabel(self.tr("Newtype"), self)
        self._newtype_label.setMinimumWidth(70)
        self._newtype_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        _nt_map = {0: "－", 1: "1", 2: "2", 3: "3"}
        self._newtype_spin = MappingCompSpin("newtype", mapping=_nt_map, parent=self)
        self._newtype_spin.setMinimumWidth(70)
        self._newtype_spin.dataChanged.connect(self.panelDataChanged)

        self._aura_label = BodyLabel(self.tr("Aura"), self)
        self._aura_label.setMinimumWidth(70)
        self._aura_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._aura_spin = MappingCompSpin("aura", mapping=_nt_map, parent=self)
        self._aura_spin.setMinimumWidth(72)
        self._aura_spin.dataChanged.connect(self.panelDataChanged)

        self._encost_label = BodyLabel(self.tr("EN cost"), self)
        self._encost_label.setMinimumWidth(70)
        self._encost_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._encost_spin = NumberCompSpin("encost", value_range=(0, 250), parent=self)
        self._encost_spin.setFixedWidth(65)
        self._encost_spin.dataChanged.connect(self.panelDataChanged)

        self._ammo_label = BodyLabel(self.tr("Ammo cnt"), self)
        self._ammo_label.setMinimumWidth(70)
        self._ammo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._ammo_spin = AmmoSpin(value_range=(0, 99), parent=self)
        self._ammo_spin.setFixedWidth(65)
        self._ammo_spin.dataChanged.connect(self.panelDataChanged)

        self._custom_label = BodyLabel(self.tr("Type"), self)
        self._custom_label.setMinimumWidth(70)
        self._custom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._custom_combo = MappingComboBox("custom", mapping={0: "[A]", 1: "[B]", 2: "[C]", 3: "[D]"}, parent=self)
        self._custom_combo.setFixedWidth(65)
        self._custom_combo.dataChanged.connect(self.panelDataChanged)

        self._bonus_label = BodyLabel(self.tr("Bonus"), self)
        self._bonus_label.setMinimumWidth(70)
        self._bonus_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._bonus_combo = MappingComboBox("bonus", mapping={i: f"[{i:X}]" for i in range(16)}, parent=self)
        self._bonus_combo.setFixedWidth(207)
        self._bonus_combo.apply_font(JP_FONT)
        self._bonus_combo.set_dropdown_font(JP_QFONT)
        self._bonus_combo.dataChanged.connect(self.panelDataChanged)

        self._attr_label = BodyLabel(self.tr("Attribute"), self)
        self._attr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._attr_label.setMinimumWidth(70)

        # ========== 网格布局 ==========

        _grid = QGridLayout()
        _grid.setSpacing(4)
        # 第 0 行：标签 + 属性位多选
        _grid.addWidget(self._attr_label, 0, 0, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._attr_combo, 0, 1, 1, 7)
        # 第 1 行：四组 label+spin 横行排列
        _grid.addWidget(self._hit_label, 1, 0, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._hit_spin, 1, 1)
        _grid.addWidget(self._crt_label, 1, 2, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._crt_spin, 1, 3)
        _grid.addWidget(self._rngs_label, 1, 4, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._rngs_spin, 1, 5)
        _grid.addWidget(self._rngl_label, 1, 6, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._rngl_spin, 1, 7)
        # 第 2 行：EN消耗 + 三组需求编辑框
        _grid.addWidget(self._encost_label, 2, 0, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._encost_spin, 2, 1)
        _grid.addWidget(self._morale_label, 2, 2, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._morale_spin, 2, 3)
        _grid.addWidget(self._newtype_label, 2, 4, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._newtype_spin, 2, 5)
        _grid.addWidget(self._aura_label, 2, 6, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._aura_spin, 2, 7)
        # 第 3 行：弹药数 + 改造类型
        _grid.addWidget(self._ammo_label, 3, 0, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._ammo_spin, 3, 1)
        _grid.addWidget(self._custom_label, 3, 2, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._custom_combo, 3, 3)
        # 第 3 行余列：改造追加
        _grid.addWidget(self._bonus_label, 3, 4, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._bonus_combo, 3, 5, 1, 3)
        self.viewLayout.addLayout(_grid)
        self.viewLayout.addStretch()
        self.setFixedWidth(564)

    # ========== UnitPanel 转发接口 ==========

    def set_model(self, model: BaseTableModel) -> None:
        """注入数据模型，监听第 0 列变更以刷新 bonus 映射"""
        self._model = model
        self._attr_combo.set_model(model)
        self._rngs_spin.set_model(model)
        self._rngl_spin.set_model(model)
        self._hit_spin.set_model(model)
        self._crt_spin.set_model(model)
        self._morale_spin.set_model(model)
        self._newtype_spin.set_model(model)
        self._aura_spin.set_model(model)
        self._encost_spin.set_model(model)
        self._ammo_spin.set_model(model)
        self._custom_combo.set_model(model)
        self._bonus_combo.set_model(model)
        # 监听第 0 列（武器名）变更
        model.dataChanged.connect(self._on_data_changed)

    def set_row(self, row: int) -> None:
        """切换行数据"""
        self._row = row
        self._attr_combo.set_row(row)
        self._rngs_spin.set_row(row)
        self._rngl_spin.set_row(row)
        self._hit_spin.set_row(row)
        self._crt_spin.set_row(row)
        self._morale_spin.set_row(row)
        self._newtype_spin.set_row(row)
        self._aura_spin.set_row(row)
        self._encost_spin.set_row(row)
        self._ammo_spin.set_row(row)
        self._custom_combo.set_row(row)
        self._bonus_combo.set_row(row)
        self._update_bonus_mapping()

    def translateUI(self) -> None:
        """刷新卡片标题和标签"""
        self.setTitle(self.tr("Weapon Details"))
        self._attr_label.setText(self.tr("Attribute"))
        self._attr_combo.set_values(EnumData().WEAPON["ATTRIBUTE"])
        self._rngs_label.setText(self.tr("Short rng"))
        self._rngl_label.setText(self.tr("Long rng"))
        self._hit_label.setText(self.tr("Accuracy"))
        self._crt_label.setText(self.tr("Critical"))
        self._morale_label.setText(self.tr("Morale"))
        self._newtype_label.setText(self.tr("Newtype"))
        self._aura_label.setText(self.tr("Aura"))
        self._encost_label.setText(self.tr("EN cost"))
        self._ammo_label.setText(self.tr("Ammo cnt"))
        self._custom_label.setText(self.tr("Type"))
        self._bonus_label.setText(self.tr("Bonus"))

    def resetUI(self) -> None:
        """刷新字体"""
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
        setFont(self._rngs_label)
        setFont(self._rngl_label)
        setFont(self._hit_label)
        setFont(self._crt_label)
        setFont(self._morale_label)
        setFont(self._newtype_label)
        setFont(self._aura_label)
        setFont(self._encost_label)
        setFont(self._ammo_label)
        setFont(self._custom_label)
        setFont(self._attr_label)
        setFont(self._bonus_label)
        self._attr_combo.resetUI()
        self._rngs_spin.resetUI()
        self._rngl_spin.resetUI()
        self._hit_spin.resetUI()
        self._crt_spin.resetUI()
        self._morale_spin.resetUI()
        self._newtype_spin.resetUI()
        self._aura_spin.resetUI()
        self._encost_spin.resetUI()
        self._ammo_spin.resetUI()
        self._custom_combo.resetUI()
        self._bonus_combo.resetUI()
        self._bonus_combo.apply_font(JP_FONT)
        self._bonus_combo.set_dropdown_font(JP_QFONT)

    # ========== 动态 bonus 映射 ==========

    def _on_data_changed(self, top_left, bottom_right, roles):
        """第 0 列数据变更时刷新 bonus 下拉选项"""
        if top_left.column() == 0 and self._row >= 0:
            self._update_bonus_mapping()

    def _update_bonus_mapping(self):
        """根据当前机体 16 武器槽刷新 bonus 映射

        每项格式: [hex]武器名，hex 为 0-F 对应槽位索引。
        """
        if self._model is None or self._row < 0:
            return
        row_count = self._model.rowCount()
        mapping = {0: "——"}  # 值 0 = 无
        for i in range(1, min(16, row_count)):
            if i == self._row:
                continue  # 跳过当前武器自身
            wname = self._model.get_row_data(i).get("wname", "")
            if not wname:
                continue  # 空武器槽跳过
            mapping[i] = f"[{i:X}]{wname}"
        self._bonus_combo.set_mapping(mapping)

class WeaponMapCard(CardHeader):
    """地图武器卡片 - 地图武器参数"""

    def __init__(self, parent=None):
        """初始化地图武器卡片"""
        super().__init__(parent)
        self.setTitle(self.tr("Map Weapon"))

        # ========== 控件 ==========

        self._mcls_label = BodyLabel(self.tr("Map class"), self)
        self._mcls_label.setMinimumWidth(64)
        self._mcls_combo = MappingComboBox("mcls", mapping=EnumData().WEAPON["MCLASS"], parent=self)
        self._mcls_combo.setMinimumWidth(160)
        self._mcls_combo.dataChanged.connect(self.panelDataChanged)

        self._mshow_label = BodyLabel(self.tr("Map show"), self)
        self._mshow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mshow_label.setMinimumWidth(64)
        self._mshow_spin = NumberCompSpin("mshow", value_range=(0, 79), parent=self)
        self._mshow_spin.setFixedWidth(70)
        self._mshow_spin.dataChanged.connect(self.panelDataChanged)

        self._radius_label = BodyLabel(self.tr("Blast radius"), self)
        self._radius_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._radius_label.setMinimumWidth(64)
        self._radius_spin = NumberCompSpin("radius", value_range=(0, 4), parent=self)
        self._radius_spin.setFixedWidth(70)
        self._radius_spin.dataChanged.connect(self.panelDataChanged)

        self._mrng_label = BodyLabel(self.tr("Directional range"), self)
        self._mrng_label.setMinimumWidth(64)
        self._mrng_combo = RangeComboBox("mrng", parent=self)
        self._mrng_combo.setMinimumWidth(200)
        self._mrng_combo.dataChanged.connect(self.panelDataChanged)

        # ========== 网格布局 ==========

        _grid = QGridLayout()
        _grid.setSpacing(4)
        _grid.setHorizontalSpacing(9)
        _grid.addWidget(self._mcls_label, 0, 0, 1, 2, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        _grid.addWidget(self._mrng_label, 0, 2, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        _grid.addWidget(self._mcls_combo, 1, 0, 1, 2)
        _grid.addWidget(self._mshow_label, 2, 0, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._mshow_spin, 2, 1)
        _grid.addWidget(self._radius_label, 3, 0, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._radius_spin, 3, 1)
        _grid.addWidget(self._mrng_combo, 1, 2, 3, 1)
        self.viewLayout.addLayout(_grid)
        self.viewLayout.addStretch()

        # ========== 地图分类联动 ==========

        self._mcls_combo.dataChanged.connect(self._on_mcls_changed)

    # ========== UnitPanel 转发接口 ==========

    def set_model(self, model: BaseTableModel) -> None:
        """注入数据模型"""
        self._model = model
        self._mcls_combo.set_model(model)
        self._mshow_spin.set_model(model)
        self._radius_spin.set_model(model)
        self._mrng_combo.set_model(model)

    def set_row(self, row: int) -> None:
        """切换行数据"""
        self._row = row
        self._mcls_combo.set_row(row)
        self._mshow_spin.set_row(row)
        self._radius_spin.set_row(row)
        self._mrng_combo.set_row(row)
        self._update_map_enable()

    def _on_mcls_changed(self, _field: str) -> None:
        """地图分类变更时刷新各控件启用状态"""
        self._update_map_enable()

    def _update_map_enable(self) -> None:
        """根据 mcls 值控制各控件的启用/禁用

        0(一一): mshow禁用, radius禁用, mrng禁用
        1(Directional): mshow启用, radius禁用, mrng启用
        2(Self Circle): mshow启用, radius禁用, mrng禁用
        3(Target Circle): mshow启用, radius启用, mrng禁用
        """
        if self._model is None or self._row < 0:
            return
        mcls = self._model.get_row_data(self._row).get("mcls", 0)
        self._mshow_spin.setEnabled(mcls != 0)
        self._radius_spin.setEnabled(mcls == 3)
        self._mrng_combo.setEnabled(mcls == 1)

    def translateUI(self) -> None:
        """刷新卡片标题和标签"""
        self.setTitle(self.tr("Map Weapon"))
        self._mcls_label.setText(self.tr("Map class"))
        self._mcls_combo.set_mapping(EnumData().WEAPON["MCLASS"])
        self._mshow_label.setText(self.tr("Map show"))
        self._radius_label.setText(self.tr("Blast radius"))
        self._mrng_label.setText(self.tr("Directional range"))

    def resetUI(self) -> None:
        """刷新字体"""
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
        setFont(self._mcls_label)
        setFont(self._mshow_label)
        setFont(self._radius_label)
        setFont(self._mrng_label)
        self._mcls_combo.resetUI()
        self._mshow_spin.resetUI()
        self._radius_spin.resetUI()
        self._mrng_combo.resetUI()


class WeaponAdaptCard(CardHeader):
    """地形适应卡片 - 四项地形适性竖直排列"""

    def __init__(self, parent=None):
        """初始化地形适应卡片"""
        super().__init__(parent)
        self.setTitle(self.tr("Terrain"))

        # ========== 控件 ==========

        _adapt_mapping = EnumData().WEAPON["ADAPT"]
        _align = Qt.AlignmentFlag.AlignCenter

        self._air_label = BodyLabel(self.tr("Air"), self)
        self._air_label.setAlignment(_align)
        self._air_label.setFixedWidth(55)
        self._air_spin = MappingCompSpin("air", mapping=_adapt_mapping, parent=self)
        self._air_spin.setMinimumWidth(70)
        self._air_spin.dataChanged.connect(self.panelDataChanged)

        self._grd_label = BodyLabel(self.tr("Lnd"), self)
        self._grd_label.setAlignment(_align)
        self._grd_label.setFixedWidth(55)
        self._grd_spin = MappingCompSpin("grd", mapping=_adapt_mapping, parent=self)
        self._grd_spin.setMinimumWidth(70)
        self._grd_spin.dataChanged.connect(self.panelDataChanged)

        self._wtr_label = BodyLabel(self.tr("Sea"), self)
        self._wtr_label.setAlignment(_align)
        self._wtr_label.setFixedWidth(55)
        self._wtr_spin = MappingCompSpin("wtr", mapping=_adapt_mapping, parent=self)
        self._wtr_spin.setMinimumWidth(70)
        self._wtr_spin.dataChanged.connect(self.panelDataChanged)

        self._spc_label = BodyLabel(self.tr("Spc"), self)
        self._spc_label.setAlignment(_align)
        self._spc_label.setFixedWidth(55)
        self._spc_spin = MappingCompSpin("spc", mapping=_adapt_mapping, parent=self)
        self._spc_spin.setMinimumWidth(70)
        self._spc_spin.dataChanged.connect(self.panelDataChanged)

        # ========== 竖直布局 ==========

        _grid = QGridLayout()
        _grid.setSpacing(4)
        _grid.setHorizontalSpacing(10)
        for i, (label, spin) in enumerate([
            (self._air_label, self._air_spin),
            (self._grd_label, self._grd_spin),
            (self._wtr_label, self._wtr_spin),
            (self._spc_label, self._spc_spin),
        ]):
            _grid.addWidget(label, i, 0, Qt.AlignmentFlag.AlignCenter)
            _grid.addWidget(spin, i, 1, Qt.AlignmentFlag.AlignCenter)
        self.viewLayout.addLayout(_grid)
        self.viewLayout.addStretch()

    # ========== UnitPanel 转发接口 ==========

    def set_model(self, model: BaseTableModel) -> None:
        """注入数据模型，转发至各子编辑器"""
        self._air_spin.set_model(model)
        self._grd_spin.set_model(model)
        self._wtr_spin.set_model(model)
        self._spc_spin.set_model(model)

    def set_row(self, row: int) -> None:
        """切换行并刷新所有控件"""
        self._air_spin.set_row(row)
        self._grd_spin.set_row(row)
        self._wtr_spin.set_row(row)
        self._spc_spin.set_row(row)

    def translateUI(self) -> None:
        """刷新卡片标题和标签"""
        self.setTitle(self.tr("Terrain"))
        self._air_label.setText(self.tr("Air"))
        self._grd_label.setText(self.tr("Lnd"))
        self._wtr_label.setText(self.tr("Sea"))
        self._spc_label.setText(self.tr("Spc"))

    def resetUI(self) -> None:
        """刷新字体"""
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
        for label in [self._air_label, self._grd_label, self._wtr_label, self._spc_label]:
            setFont(label)


# =============================================================================
# 面板容器
# =============================================================================


class WeaponPanel(ProxyFrame):
    """武器右侧面板 - 3 张卡片上下 hbox 布局"""

    def __init__(self, parent=None):
        """初始化武器面板"""
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)

        # ========== 创建卡片 ==========

        self._attr_card = WeaponAttrCard(self)
        self._map_card = WeaponMapCard(self)
        self._adapt_card = WeaponAdaptCard(self)

        # ========== 上下两行 hbox 布局 ==========

        _top = QHBoxLayout()
        _top.setSpacing(8)
        _top.addWidget(self._attr_card)

        _bottom = QHBoxLayout()
        _bottom.setSpacing(8)
        _bottom.addWidget(self._map_card)
        _bottom.addWidget(self._adapt_card)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addLayout(_top)
        layout.addLayout(_bottom)
        layout.addStretch()
        self.setLayout(layout)

    # ========== 行数据转发 ==========

    def set_model(self, model: BaseTableModel) -> None:
        """注入数据模型，转发至各卡片"""
        self._attr_card.set_model(model)
        self._map_card.set_model(model)
        self._adapt_card.set_model(model)

    def set_row(self, row: int) -> None:
        """切换行并刷新所有卡片"""
        self._attr_card.set_row(row)
        self._map_card.set_row(row)
        self._adapt_card.set_row(row)

    # ========== Theme / i18n ==========

    def translateUI(self) -> None:
        """刷新卡片标题"""
        self._attr_card.translateUI()
        self._map_card.translateUI()
        self._adapt_card.translateUI()

    def resetUI(self) -> None:
        """刷新字体"""
        self._attr_card.resetUI()
        self._map_card.resetUI()
        self._adapt_card.resetUI()
        super().resetUI()


# =============================================================================
# 框架（表格 + 面板）
# =============================================================================


class WeaponFrame(ProxyFrame):
    """武器编辑框架 - 武器表格 + 右侧面板

    内部布局：WeaponView（表格）在左，WeaponPanel（面板）在右。
    面板始终显示，不再支持折叠。
    """

    def __init__(self, parent=None):
        """初始化武器编辑框架"""
        super().__init__(parent)

        # ========== 武器表格 ==========

        self._weapon_view = WeaponView(self)
        self._weapon_view.sClicked.connect(self._on_weapon_row_clicked)

        # ========== 右侧面板 ==========

        self._weapon_panel = WeaponPanel(self)

    # ========== 布局 ==========

    def _update_layout(self):
        """重算表格和面板的位置"""
        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return

        # 表格占据左侧（所有列），面板占据右侧剩余空间
        table_w = self._weapon_view.get_content_width(False) - 10
        panel_w = max(0, w - table_w)
        self._weapon_view.setGeometry(0, 0, table_w, h)
        self._weapon_panel.setGeometry(table_w, 0, panel_w, h)

    def resizeEvent(self, event):
        """尺寸变化时刷新布局"""
        super().resizeEvent(event)
        self._update_layout()

    # ========== 行选择 ==========

    def _on_weapon_row_clicked(self, source_row: int, model: BaseTableModel) -> None:
        """武器行单击时刷新面板卡片

        Args:
            source_row: 源模型行号
            model:      BaseTableModel 实例
        """
        self._weapon_panel.set_row(source_row)

    # ========== 数据接口 ==========

    def set_data(self, data: list[dict]) -> None:
        """装入武器列表数据并选中第一行

        Args:
            data: robots[N]["weapons"] 武器数据列表
        """
        self._weapon_view.set_data(data)

        # 将武器表格模型注入面板卡片
        model = self._weapon_view.source_model()
        self._weapon_panel.set_model(model)

        # 默认选中第一行
        if model.rowCount() > 0:
            self._weapon_view.select_source_row(0)
            self._on_weapon_row_clicked(0, model)

        self._update_layout()

    def set_field(self, fields) -> None:
        """设置字段映射，代理至武器表格模型

        Args:
            fields: FieldMapping 实例
        """
        self._weapon_view.set_field(fields)

    # ========== Theme / i18n ==========

    def translateUI(self) -> None:
        """刷新子控件翻译"""
        self._weapon_view.translateUI()
        self._weapon_panel.translateUI()
        # 翻译后列宽可能变化，重新布局
        self._update_layout()

    def resetUI(self) -> None:
        """刷新子控件字体"""
        self._weapon_view.resetUI()
        self._weapon_panel.resetUI()
        super().resetUI()
