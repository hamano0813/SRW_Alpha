"""
地图武器卡片

提供地图武器分类、地图武器演出、爆风半径、覆盖范围编辑。
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGridLayout, QSizePolicy
from qfluentwidgets import setFont

from gui.custom.enums import EnumData
from gui.widget import (
    CardHeader,
    CommonMappingCombo,
    CommonNumberSpin,
    CommonStretchLabel,
    RangeCombo,
)


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

    def set_row(self, row: int) -> None:
        super().set_row(row)
        self._mcls_combo.set_value(self._read("mcls"))
        self._update_map_enable()
        self._mshow_combo.set_value(self._read("mshow"))
        self._radius_spin.set_value(self._read("radius"))
        self._mrng_combo.set_value(self._read("mrng"))

    def _on_mcls_value_changed(self, value: int) -> None:
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
