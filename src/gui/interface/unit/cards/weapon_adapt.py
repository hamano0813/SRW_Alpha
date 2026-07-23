"""
武器地形适应卡片

四项地形适性 MappingSpin 竖直排列。
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGridLayout
from qfluentwidgets import setFont

from gui.custom.enums import EnumData
from gui.widget import (
    CardHeader,
    CommonMappingSpin,
    CommonStretchLabel,
)


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
