"""
驾驶员特殊技能卡片

提供特殊技能 Bit 位多选列表编辑。
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSizePolicy
from qfluentwidgets import setFont

from gui.custom import EnumData
from gui.widget import CardHeader, CommonBitList


class SpecialSkillsCard(CardHeader):
    """特殊技能卡片 - Bit 位多选特殊技能列表"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Special skills"))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self._skills_list = CommonBitList(parent=self)
        self._skills_list.valueChanged.connect(lambda v: self._write("skls", v))

        self.viewLayout.setContentsMargins(3, 8, 3, 8)
        self.viewLayout.addWidget(self._skills_list)

    def set_row(self, row: int) -> None:
        super().set_row(row)
        self._skills_list.set_value(self._read("skls"))

    def translateUI(self) -> None:
        self.setTitle(self.tr("Special skills"))
        self._skills_list.set_values(EnumData().PILOT["SKILL"])

    def resetUI(self) -> None:
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
        self._skills_list.resetUI()
