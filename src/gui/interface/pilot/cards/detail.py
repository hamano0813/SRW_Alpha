"""
驾驶员详细信息卡片（占位）

提供驾驶员姓名、头像等基本信息的编辑区。
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSizePolicy
from qfluentwidgets import setFont

from gui.widget import CardHeader


class PilotDetailCard(CardHeader):
    """驾驶员详细信息卡片（占位）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Pilot Detail"))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    def translateUI(self) -> None:
        self.setTitle(self.tr("Pilot Detail"))

    def resetUI(self) -> None:
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
