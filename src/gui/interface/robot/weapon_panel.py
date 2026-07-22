"""
武器编辑子框架 - 武器表格 + 右侧面板

包含 WeaponView（武器表格）和 3 张编辑卡片。

Classes:
    WeaponAttrCard:    武器属性卡片（含射程/命中/会心/需求）
    WeaponMapCard:     地图武器卡片
    WeaponAdaptCard:   地形适应卡片（空陆海宇）
    WeaponPanel:    右侧面板容器
    WeaponFrame:    武器编辑框架
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QSizePolicy, QVBoxLayout
from qfluentwidgets import setFont

from gui.custom.enums import EnumData
from gui.custom.fonts import JP_FONT, JP_QFONT
from gui.widget import (
    BaseTableModel,
    CardHeader,
    CommonBitCombo,
    CommonMappingCombo,
    CommonMappingSpin,
    CommonNumberSpin,
    CommonStretchLabel,
    ProxyFrame,
    RangeCombo,
)

from .weapon_frame import WeaponView


class WeaponAttrCard(CardHeader):
    """武器属性卡片 - 武器属性 + 其他参数"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Weapon Details"))

        self._attr_combo = CommonBitCombo(values=EnumData().WEAPON["ATTRIBUTE"], sep=" / ", parent=self)
        self._attr_combo.valueChanged.connect(lambda v: self._write("attr", v))

        self._rngs_label = CommonStretchLabel(self.tr("Short rng"), self)
        self._rngs_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._rngs_spin = CommonNumberSpin(value_range=(0, 3), parent=self)
        self._rngs_spin.valueChanged.connect(lambda v: self._write("rngs", v))

        self._rngl_label = CommonStretchLabel(self.tr("Long rng"), self)
        self._rngl_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._rngl_spin = CommonNumberSpin(value_range=(0, 15), parent=self)
        self._rngl_spin.valueChanged.connect(lambda v: self._write("rngl", v))

        self._hit_label = CommonStretchLabel(self.tr("Accuracy"), self)
        self._hit_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._hit_spin = CommonNumberSpin(value_range=(-99, 99), show_sign=True, parent=self)
        self._hit_spin.valueChanged.connect(lambda v: self._write("hit", v))

        self._crt_label = CommonStretchLabel(self.tr("Critical"), self)
        self._crt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._crt_spin = CommonNumberSpin(value_range=(-99, 99), show_sign=True, parent=self)
        self._crt_spin.valueChanged.connect(lambda v: self._write("crt", v))

        self._morale_label = CommonStretchLabel(self.tr("Morale"), self)
        self._morale_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._morale_spin = CommonNumberSpin(value_range=(0, 150), parent=self)
        self._morale_spin.valueChanged.connect(lambda v: self._write("morale", v))

        self._newtype_label = CommonStretchLabel(self.tr("Newtype"), self)
        self._newtype_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        _nt_map = {0: "－", 1: "1", 2: "2", 3: "3"}
        self._newtype_spin = CommonMappingSpin(mapping=_nt_map, parent=self)
        self._newtype_spin.valueChanged.connect(lambda v: self._write("newtype", v))

        self._aura_label = CommonStretchLabel(self.tr("Aura"), self)
        self._aura_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._aura_spin = CommonMappingSpin(mapping=_nt_map, parent=self)
        self._aura_spin.valueChanged.connect(lambda v: self._write("aura", v))

        self._encost_label = CommonStretchLabel(self.tr("EN cost"), self)
        self._encost_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._encost_spin = CommonNumberSpin(value_range=(0, 250), parent=self)
        self._encost_spin.valueChanged.connect(lambda v: self._write("encost", v))

        self._ammo_label = CommonStretchLabel(self.tr("Ammo cnt"), self)
        self._ammo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._ammo_spin = CommonNumberSpin(value_range=(0, 99), parent=self)
        self._ammo_spin.valueChanged.connect(self._on_ammo_changed)

        self._custom_label = CommonStretchLabel(self.tr("Type"), self)
        self._custom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._custom_combo = CommonMappingSpin(mapping={0: "[A]", 1: "[B]", 2: "[C]", 3: "[D]"}, parent=self)
        self._custom_combo.valueChanged.connect(lambda v: self._write("custom", v))

        self._bonus_label = CommonStretchLabel(self.tr("Bonus"), self)
        self._bonus_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._bonus_combo = CommonMappingCombo(mapping={i: f"[{i:X}]" for i in range(16)}, parent=self)
        self._bonus_combo.apply_font(JP_FONT)
        self._bonus_combo.set_dropdown_font(JP_QFONT)
        self._bonus_combo.valueChanged.connect(lambda v: self._write("bonus", v))

        self._attr_label = CommonStretchLabel(self.tr("Attribute"), self)
        self._attr_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        _grid = QGridLayout()
        _grid.setSpacing(4)
        _grid.addWidget(self._attr_label, 0, 0, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._attr_combo, 0, 1, 1, 7)
        _grid.addWidget(self._hit_label, 1, 0, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._hit_spin, 1, 1)
        _grid.addWidget(self._crt_label, 1, 2, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._crt_spin, 1, 3)
        _grid.addWidget(self._rngs_label, 1, 4, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._rngs_spin, 1, 5)
        _grid.addWidget(self._rngl_label, 1, 6, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._rngl_spin, 1, 7)
        _grid.addWidget(self._encost_label, 2, 0, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._encost_spin, 2, 1)
        _grid.addWidget(self._morale_label, 2, 2, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._morale_spin, 2, 3)
        _grid.addWidget(self._newtype_label, 2, 4, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._newtype_spin, 2, 5)
        _grid.addWidget(self._aura_label, 2, 6, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._aura_spin, 2, 7)
        _grid.addWidget(self._ammo_label, 3, 0, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._ammo_spin, 3, 1)
        _grid.addWidget(self._custom_label, 3, 2, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._custom_combo, 3, 3)
        _grid.addWidget(self._bonus_label, 3, 4, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._bonus_combo, 3, 5, 1, 3)
        self.viewLayout.addLayout(_grid)
        self.viewLayout.addStretch()

    # ========== 数据接口 ==========

    def set_model(self, model: BaseTableModel) -> None:
        super().set_model(model)
        model.dataChanged.connect(self._on_data_changed)

    def set_row(self, row: int) -> None:
        super().set_row(row)
        self._attr_combo.set_value(self._read("attr"))
        self._rngs_spin.set_value(self._read("rngs"))
        self._rngl_spin.set_value(self._read("rngl"))
        self._hit_spin.set_value(self._read("hit"))
        self._crt_spin.set_value(self._read("crt"))
        self._morale_spin.set_value(self._read("morale"))
        self._newtype_spin.set_value(self._read("newtype"))
        self._aura_spin.set_value(self._read("aura"))
        self._encost_spin.set_value(self._read("encost"))
        self._ammo_spin.set_value(self._read("ammom"))
        self._custom_combo.set_value(self._read("custom"))
        self._bonus_combo.set_value(self._read("bonus"))
        self._update_bonus_mapping()

    # ========== 弹药双字段写回 ==========

    def _on_ammo_changed(self, value: int) -> None:
        """弹药变更时同步写入 ammod 和 ammom"""
        if self._model is not None and self._row >= 0:
            row_data = self._model.get_row_data(self._row)
            row_data["ammod"] = value
            row_data["ammom"] = value
        self.panelDataChanged.emit("ammom")

    # ========== 动态 bonus 映射 ==========

    def _on_data_changed(self, top_left, bottom_right, roles):
        """第 0 列数据变更时刷新 bonus 下拉选项"""
        if top_left.column() == 0 and self._row >= 0:
            self._update_bonus_mapping()

    def _update_bonus_mapping(self):
        if self._model is None or self._row < 0:
            return
        row_count = self._model.rowCount()
        mapping: dict[int, str] = {0: "——"}
        for i in range(1, min(16, row_count)):
            if i == self._row:
                continue
            wname = self._model.get_row_data(i).get("wname", "")
            if not wname:
                continue
            mapping[i] = f"[{i:X}]{wname}"
        self._bonus_combo.set_mapping(mapping)

    # ========== UI 刷新 ==========

    def translateUI(self) -> None:
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
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
        for lbl in [self._rngs_label, self._rngl_label, self._hit_label,
                     self._crt_label, self._morale_label, self._newtype_label,
                     self._aura_label, self._encost_label, self._ammo_label,
                     self._custom_label, self._attr_label, self._bonus_label]:
            setFont(lbl)
        for w in [self._attr_combo, self._rngs_spin, self._rngl_spin,
                   self._hit_spin, self._crt_spin, self._morale_spin,
                   self._newtype_spin, self._aura_spin, self._encost_spin,
                   self._ammo_spin, self._custom_combo, self._bonus_combo]:
            w.resetUI()
        self._bonus_combo.apply_font(JP_FONT)
        self._bonus_combo.set_dropdown_font(JP_QFONT)


class WeaponMapCard(CardHeader):
    """地图武器卡片 - 地图武器参数"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Map Weapon"))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self._mcls_label = CommonStretchLabel(self.tr("Map class"), self)
        self._mcls_combo = CommonMappingCombo(mapping=EnumData().WEAPON["MCLASS"], parent=self)

        self._mshow_label = CommonStretchLabel(self.tr("Map show"), self)
        self._mshow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._mshow_combo = CommonMappingCombo(mapping={i: f"[{i:02X}]" for i in range(80)}, parent=self)

        self._radius_label = CommonStretchLabel(self.tr("Blast radius"), self)
        self._radius_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._radius_spin = CommonNumberSpin(value_range=(0, 4), parent=self)

        self._mrng_combo = RangeCombo(parent=self)

        # 数据回写
        self._mcls_combo.valueChanged.connect(self._on_mcls_value_changed)
        self._mshow_combo.valueChanged.connect(lambda v: self._write("mshow", v))
        self._radius_spin.valueChanged.connect(lambda v: self._write("radius", v))
        self._mrng_combo.valueChanged.connect(lambda v: self._write("mrng", v))

        _grid = QGridLayout()
        _grid.setSpacing(4)
        _grid.setHorizontalSpacing(9)
        _grid.addWidget(self._mcls_label, 0, 0, 1, 2, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        _grid.addWidget(self._mcls_combo, 1, 0, 1, 2)
        _grid.addWidget(self._mshow_label, 2, 0, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._mshow_combo, 2, 1)
        _grid.addWidget(self._radius_label, 3, 0, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._radius_spin, 3, 1)
        _grid.addWidget(self._mrng_combo, 0, 2, 4, 1)
        self.viewLayout.addLayout(_grid)
        self.viewLayout.addStretch()

    # ========== 数据接口 ==========

    def set_row(self, row: int) -> None:
        super().set_row(row)
        self._mcls_combo.set_value(self._read("mcls"))
        self._update_map_enable()
        self._mshow_combo.set_value(self._read("mshow"))
        self._radius_spin.set_value(self._read("radius"))
        self._mrng_combo.set_value(self._read("mrng"))

    def _on_mcls_value_changed(self, value: int) -> None:
        """mcls 变更时写回并触发联动"""
        self._write("mcls", value)
        self._update_map_enable()

    def _update_map_enable(self) -> None:
        mcls = self._read("mcls") or 0
        self._mshow_combo.setEnabled(mcls != 0)
        self._radius_spin.setEnabled(mcls == 3)
        self._mrng_combo.setEnabled(mcls == 1)

    def translateUI(self) -> None:
        self.setTitle(self.tr("Map Weapon"))
        self._mcls_label.setText(self.tr("Map class"))
        self._mcls_combo.set_mapping(EnumData().WEAPON["MCLASS"])
        self._mshow_label.setText(self.tr("Map show"))
        self._radius_label.setText(self.tr("Blast radius"))

    def resetUI(self) -> None:
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
        setFont(self._mcls_label)
        setFont(self._mshow_label)
        setFont(self._radius_label)
        self._mcls_combo.resetUI()
        self._mshow_combo.resetUI()
        self._radius_spin.resetUI()
        self._mrng_combo.resetUI()


class WeaponAdaptCard(CardHeader):
    """地形适应卡片 - 四项地形适性竖直排列"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Terrain"))

        _adapt_mapping = EnumData().WEAPON["ADAPT"]

        self._air_label = CommonStretchLabel(self.tr("Air"), self)
        self._air_label.setFixedWidth(40)
        self._air_spin = CommonMappingSpin(mapping=_adapt_mapping, parent=self)
        self._air_spin.valueChanged.connect(lambda v: self._write("air", v))

        self._grd_label = CommonStretchLabel(self.tr("Lnd"), self)
        self._grd_label.setFixedWidth(40)
        self._grd_spin = CommonMappingSpin(mapping=_adapt_mapping, parent=self)
        self._grd_spin.valueChanged.connect(lambda v: self._write("grd", v))

        self._wtr_label = CommonStretchLabel(self.tr("Sea"), self)
        self._wtr_label.setFixedWidth(40)
        self._wtr_spin = CommonMappingSpin(mapping=_adapt_mapping, parent=self)
        self._wtr_spin.valueChanged.connect(lambda v: self._write("wtr", v))

        self._spc_label = CommonStretchLabel(self.tr("Spc"), self)
        self._spc_label.setFixedWidth(40)
        self._spc_spin = CommonMappingSpin(mapping=_adapt_mapping, parent=self)
        self._spc_spin.valueChanged.connect(lambda v: self._write("spc", v))

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

    def set_row(self, row: int) -> None:
        super().set_row(row)
        self._air_spin.set_value(self._read("air"))
        self._grd_spin.set_value(self._read("grd"))
        self._wtr_spin.set_value(self._read("wtr"))
        self._spc_spin.set_value(self._read("spc"))

    def translateUI(self) -> None:
        self.setTitle(self.tr("Terrain"))
        self._air_label.setText(self.tr("Air"))
        self._grd_label.setText(self.tr("Lnd"))
        self._wtr_label.setText(self.tr("Sea"))
        self._spc_label.setText(self.tr("Spc"))

    def resetUI(self) -> None:
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
        for label in [self._air_label, self._grd_label, self._wtr_label, self._spc_label]:
            setFont(label)


class WeaponPanel(ProxyFrame):
    """武器右侧面板 - 3 张卡片上下 hbox 布局"""

    panelDataChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self._attr_card = WeaponAttrCard(self)
        self._attr_card.panelDataChanged.connect(self.panelDataChanged)
        self._map_card = WeaponMapCard(self)
        self._map_card.panelDataChanged.connect(self.panelDataChanged)
        self._adapt_card = WeaponAdaptCard(self)
        self._adapt_card.panelDataChanged.connect(self.panelDataChanged)

        _top = QHBoxLayout()
        _top.setSpacing(8)
        _top.addWidget(self._attr_card)

        _bottom = QHBoxLayout()
        _bottom.setSpacing(8)
        _bottom.addWidget(self._map_card)
        _bottom.addWidget(self._adapt_card)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(_top)
        layout.addLayout(_bottom)
        layout.addStretch()
        self.setLayout(layout)

    def set_model(self, model: BaseTableModel) -> None:
        self._attr_card.set_model(model)
        self._map_card.set_model(model)
        self._adapt_card.set_model(model)

    def set_row(self, row: int) -> None:
        self._attr_card.set_row(row)
        self._map_card.set_row(row)
        self._adapt_card.set_row(row)

    def translateUI(self) -> None:
        self._attr_card.translateUI()
        self._map_card.translateUI()
        self._adapt_card.translateUI()

    def resetUI(self) -> None:
        self._attr_card.resetUI()
        self._map_card.resetUI()
        self._adapt_card.resetUI()
        super().resetUI()


class WeaponFrame(ProxyFrame):
    """武器编辑框架 - 武器表格 + 右侧面板"""

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setSpacing(8)

        self._weapon_view = WeaponView(self)
        self._weapon_view.sClicked.connect(self._on_weapon_row_clicked)
        layout.addWidget(self._weapon_view)

        self._weapon_panel = WeaponPanel(self)
        layout.addWidget(self._weapon_panel)

    def _on_weapon_row_clicked(self, source_row: int, model: BaseTableModel) -> None:
        self._weapon_panel.set_row(source_row)

    def set_data(self, data: list[dict]) -> None:
        self._weapon_view.set_data(data)
        model = self._weapon_view.source_model()
        self._weapon_panel.set_model(model)
        if model.rowCount() > 0:
            self._weapon_view.select_source_row(0)
            self._on_weapon_row_clicked(0, model)

    def set_field(self, fields) -> None:
        self._weapon_view.set_field(fields)

    def translateUI(self) -> None:
        self._weapon_view.translateUI()
        self._weapon_panel.translateUI()

    def resetUI(self) -> None:
        self._weapon_view.resetUI()
        self._weapon_panel.resetUI()
        super().resetUI()
