"""
地形适性卡片

提供移动类型 BitCombo + 四项地形适性 MappingSpin 编辑。
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGridLayout
from qfluentwidgets import setFont

from gui.custom.enums import EnumData
from gui.widget import (
    CardHeader,
    CommonBitCombo,
    CommonMappingSpin,
    CommonStretchLabel,
)


class TerrainCard(CardHeader):
    """地形适性卡片 - 移动类型 + 四项地形适性"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Terrain"))

        _align = Qt.AlignmentFlag.AlignCenter
        _adapt_mapping = EnumData().ROBOT["ADAPT"]

        self._move_combo = CommonBitCombo(values=[], sep="")
        self._move_combo.valueChanged.connect(lambda v: self._write("type", v))

        self._air_label = CommonStretchLabel(self.tr("Air"), self)
        self._air_label.setFixedWidth(60)
        self._air_spin = CommonMappingSpin(mapping=_adapt_mapping, parent=self)
        self._air_spin.valueChanged.connect(lambda v: self._write("air", v))

        self._grd_label = CommonStretchLabel(self.tr("Lnd"), self)
        self._grd_label.setFixedWidth(60)
        self._grd_spin = CommonMappingSpin(mapping=_adapt_mapping, parent=self)
        self._grd_spin.valueChanged.connect(lambda v: self._write("grd", v))

        self._wtr_label = CommonStretchLabel(self.tr("Sea"), self)
        self._wtr_label.setFixedWidth(60)
        self._wtr_spin = CommonMappingSpin(mapping=_adapt_mapping, parent=self)
        self._wtr_spin.valueChanged.connect(lambda v: self._write("wtr", v))

        self._spc_label = CommonStretchLabel(self.tr("Spc"), self)
        self._spc_label.setFixedWidth(60)
        self._spc_label.setAlignment(_align)
        self._spc_spin = CommonMappingSpin(mapping=_adapt_mapping, parent=self)
        self._spc_spin.valueChanged.connect(lambda v: self._write("spc", v))

        _grid = QGridLayout()
        _grid.setSpacing(4)
        _grid.setHorizontalSpacing(8)
        _grid.addWidget(self._move_combo, 0, 0, 1, 2)
        _grid.addWidget(self._air_label, 1, 0, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._air_spin, 1, 1)
        _grid.addWidget(self._grd_label, 2, 0, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._grd_spin, 2, 1)
        _grid.addWidget(self._wtr_label, 3, 0, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._wtr_spin, 3, 1)
        _grid.addWidget(self._spc_label, 4, 0, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._spc_spin, 4, 1)
        self.viewLayout.addLayout(_grid)
        self.viewLayout.addStretch()

    def set_row(self, row: int) -> None:
        super().set_row(row)
        self._move_combo.set_value(self._read("type"))
        self._air_spin.set_value(self._read("air"))
        self._grd_spin.set_value(self._read("grd"))
        self._wtr_spin.set_value(self._read("wtr"))
        self._spc_spin.set_value(self._read("spc"))

    def translateUI(self) -> None:
        self.setTitle(self.tr("Terrain"))
        _enum = EnumData()
        self._move_combo.set_values(_enum.ROBOT["MOVETYPE"])
        self._air_label.setText(self.tr("Air"))
        self._air_spin.set_mapping(_enum.ROBOT["ADAPT"])
        self._grd_label.setText(self.tr("Lnd"))
        self._grd_spin.set_mapping(_enum.ROBOT["ADAPT"])
        self._wtr_label.setText(self.tr("Sea"))
        self._wtr_spin.set_mapping(_enum.ROBOT["ADAPT"])
        self._spc_label.setText(self.tr("Spc"))
        self._spc_spin.set_mapping(_enum.ROBOT["ADAPT"])

    def resetUI(self) -> None:
        self._move_combo.resetUI()
        self._air_spin.resetUI()
        self._grd_spin.resetUI()
        self._wtr_spin.resetUI()
        self._spc_spin.resetUI()
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
        setFont(self._air_label)
        setFont(self._grd_label)
        setFont(self._wtr_label)
        setFont(self._spc_label)
