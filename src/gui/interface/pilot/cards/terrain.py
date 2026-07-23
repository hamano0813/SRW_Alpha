"""
驾驶员地形适性卡片

提供四项地形适性（空/陆/海/宇）的编辑，横排布局。
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy
from qfluentwidgets import setFont

from gui.custom import EnumData
from gui.widget import CardHeader, CommonMappingSpin, CommonStretchLabel


class TerrainCard(CardHeader):
    """地形适性卡片 - 四项地形适性横排"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Terrain"))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        _adapt = EnumData().PILOT["ADAPT"]

        self._air_label = CommonStretchLabel(self.tr("Air"), self)
        self._air_label.setFixedWidth(60)
        self._air_spin = CommonMappingSpin(mapping=_adapt, parent=self)
        self._air_spin.valueChanged.connect(lambda v: self._write("air", v))

        self._grd_label = CommonStretchLabel(self.tr("Lnd"), self)
        self._grd_label.setFixedWidth(60)
        self._grd_spin = CommonMappingSpin(mapping=_adapt, parent=self)
        self._grd_spin.valueChanged.connect(lambda v: self._write("grd", v))

        self._wtr_label = CommonStretchLabel(self.tr("Sea"), self)
        self._wtr_label.setFixedWidth(60)
        self._wtr_spin = CommonMappingSpin(mapping=_adapt, parent=self)
        self._wtr_spin.valueChanged.connect(lambda v: self._write("wtr", v))

        self._spc_label = CommonStretchLabel(self.tr("Spc"), self)
        self._spc_label.setFixedWidth(60)
        self._spc_spin = CommonMappingSpin(mapping=_adapt, parent=self)
        self._spc_spin.valueChanged.connect(lambda v: self._write("spc", v))

        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(self._air_label)
        row.addWidget(self._air_spin)
        row.addWidget(self._grd_label)
        row.addWidget(self._grd_spin)
        row.addWidget(self._wtr_label)
        row.addWidget(self._wtr_spin)
        row.addWidget(self._spc_label)
        row.addWidget(self._spc_spin)
        self.viewLayout.addLayout(row)

    def set_row(self, row: int) -> None:
        super().set_row(row)
        self._air_spin.set_value(self._read("air"))
        self._grd_spin.set_value(self._read("grd"))
        self._wtr_spin.set_value(self._read("wtr"))
        self._spc_spin.set_value(self._read("spc"))

    def translateUI(self) -> None:
        self.setTitle(self.tr("Terrain"))
        _adapt = EnumData().PILOT["ADAPT"]
        self._air_label.setText(self.tr("Air"))
        self._air_spin.set_mapping(_adapt)
        self._grd_label.setText(self.tr("Lnd"))
        self._grd_spin.set_mapping(_adapt)
        self._wtr_label.setText(self.tr("Sea"))
        self._wtr_spin.set_mapping(_adapt)
        self._spc_label.setText(self.tr("Spc"))
        self._spc_spin.set_mapping(_adapt)

    def resetUI(self) -> None:
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
