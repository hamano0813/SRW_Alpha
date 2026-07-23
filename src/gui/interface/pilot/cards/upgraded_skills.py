"""
驾驶员等级制技能卡片（占位）

提供等级制技能列表的编辑。
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSizePolicy
from qfluentwidgets import setFont

from gui.widget import CardHeader


class UpgradedSkillsCard(CardHeader):
    """等级制技能卡片（占位）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Upgraded skills"))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    def translateUI(self) -> None:
        self.setTitle(self.tr("Upgraded skills"))

    def resetUI(self) -> None:
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
