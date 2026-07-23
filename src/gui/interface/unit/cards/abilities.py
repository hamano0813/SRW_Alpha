"""
能力列表卡片

BitCheckList 位编辑，每位对应该机体的一个特殊能力。
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSizePolicy
from qfluentwidgets import setFont

from gui.custom import EnumData
from gui.widget import CardHeader, CommonBitList


class AbilitiesCard(CardHeader):
    """能力列表卡片 - Bit 位多选能力列表"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Abilities"))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self._abil_list = CommonBitList(parent=self)
        self._abil_list.valueChanged.connect(lambda v: self._write("abi", v))

        self.viewLayout.setContentsMargins(3, 8, 3, 8)
        self.viewLayout.addWidget(self._abil_list)

    def set_row(self, row: int) -> None:
        super().set_row(row)
        self._abil_list.set_value(self._read("abi"))

    def translateUI(self) -> None:
        self.setTitle(self.tr("Abilities"))
        self._abil_list.set_values(EnumData().ROBOT["ABILITIES"])

    def resetUI(self) -> None:
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
        self._abil_list.resetUI()
