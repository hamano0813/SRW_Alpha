"""
武器属性卡片

包含武器属性位选择、射程/命中/会心/气力/EN消耗/弹药/改造等编辑。
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGridLayout
from qfluentwidgets import setFont

from gui.custom import EnumData, JP_FONT, JP_QFONT
from gui.widget import (
    BaseTableModel,
    CardHeader,
    CommonBitCombo,
    CommonMappingCombo,
    CommonMappingSpin,
    CommonNumberSpin,
    CommonStretchLabel,
)


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

    def _on_ammo_changed(self, value: int) -> None:
        if self._model is not None and self._row >= 0:
            row_data = self._model.get_row_data(self._row)
            row_data["ammod"] = value
            row_data["ammom"] = value
        self.panelDataChanged.emit("ammom")

    def _on_data_changed(self, top_left, bottom_right, roles):
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
