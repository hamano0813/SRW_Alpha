"""
驾驶员侧边栏面板 - 分组卡片布局与数据编辑

提供驾驶员数据的编辑功能。各类卡片拆分为独立子类（均为占位，等待填充）。
PilotPanel 只负责编排和接口转发。

Classes:
    PilotDetailCard:   驾驶员详细信息卡片（占位）
    SpiritsCard:       精神指令卡片（占位）
    TerrainCard:       地形适性卡片（占位）
    SeriesCard:        系列卡片（占位）
    SpecialSkillsCard: 特殊技能卡片（占位）
    UpgradedSkillsCard:等级制技能卡片（占位）
    PilotPanel:        驾驶员侧边栏面板
"""

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout
from qfluentwidgets import setFont

from gui.custom.models import BaseTableModel
from gui.custom.widgets.card_header import CardHeader
from gui.custom.widgets.proxy_frame import ProxyFrame


class PilotDetailCard(CardHeader):
    """驾驶员详细信息卡片（占位）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Pilot Detail"))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    def set_model(self, model: BaseTableModel) -> None:
        """占位 - 待实现"""

    def set_row(self, row: int) -> None:
        """占位 - 待实现"""

    def translateUI(self) -> None:
        self.setTitle(self.tr("Pilot Detail"))

    def resetUI(self) -> None:
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)


class SpiritsCard(CardHeader):
    """精神指令卡片（占位）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Spirits"))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    def set_model(self, model: BaseTableModel) -> None:
        """占位 - 待实现"""

    def set_row(self, row: int) -> None:
        """占位 - 待实现"""

    def translateUI(self) -> None:
        self.setTitle(self.tr("Spirits"))

    def resetUI(self) -> None:
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)


class TerrainCard(CardHeader):
    """地形适性卡片（占位）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Terrain"))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    def set_model(self, model: BaseTableModel) -> None:
        """占位 - 待实现"""

    def set_row(self, row: int) -> None:
        """占位 - 待实现"""

    def translateUI(self) -> None:
        self.setTitle(self.tr("Terrain"))

    def resetUI(self) -> None:
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)


class SeriesCard(CardHeader):
    """系列卡片（占位）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Series"))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    def set_model(self, model: BaseTableModel) -> None:
        """占位 - 待实现"""

    def set_row(self, row: int) -> None:
        """占位 - 待实现"""

    def translateUI(self) -> None:
        self.setTitle(self.tr("Series"))

    def resetUI(self) -> None:
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)


class SpecialSkillsCard(CardHeader):
    """特殊技能卡片（占位）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Special skills"))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    def set_model(self, model: BaseTableModel) -> None:
        """占位 - 待实现"""

    def set_row(self, row: int) -> None:
        """占位 - 待实现"""

    def translateUI(self) -> None:
        self.setTitle(self.tr("Special skills"))

    def resetUI(self) -> None:
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)


class UpgradedSkillsCard(CardHeader):
    """等级制技能卡片（占位）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Upgraded skills"))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

    def set_model(self, model: BaseTableModel) -> None:
        """占位 - 待实现"""

    def set_row(self, row: int) -> None:
        """占位 - 待实现"""

    def translateUI(self) -> None:
        self.setTitle(self.tr("Upgraded skills"))

    def resetUI(self) -> None:
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)


class PilotPanel(ProxyFrame):
    """驾驶员侧边栏面板 - 分组卡片编辑区，负责布局与接口转发"""

    panelDataChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self._detail_card = PilotDetailCard(self)
        self._spirits_card = SpiritsCard(self)
        self._terrain_card = TerrainCard(self)
        self._series_card = SeriesCard(self)
        self._skills_card = SpecialSkillsCard(self)
        self._upgraded_card = UpgradedSkillsCard(self)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(self._detail_card)
        layout.addWidget(self._spirits_card)
        layout.addWidget(self._terrain_card)
        layout.addWidget(self._series_card)
        layout.addWidget(self._skills_card)
        layout.addWidget(self._upgraded_card)
        layout.addStretch()
        self.setLayout(layout)
        self.translateUI()

    # ========== 翻译 ==========

    def translateUI(self):
        self._detail_card.translateUI()
        self._spirits_card.translateUI()
        self._terrain_card.translateUI()
        self._series_card.translateUI()
        self._skills_card.translateUI()
        self._upgraded_card.translateUI()

    def resetUI(self):
        self._detail_card.resetUI()
        self._spirits_card.resetUI()
        self._terrain_card.resetUI()
        self._series_card.resetUI()
        self._skills_card.resetUI()
        self._upgraded_card.resetUI()
        super().resetUI()

    def set_model(self, model: BaseTableModel) -> None:
        self._detail_card.set_model(model)
        self._spirits_card.set_model(model)
        self._terrain_card.set_model(model)
        self._series_card.set_model(model)
        self._skills_card.set_model(model)
        self._upgraded_card.set_model(model)

    def set_row(self, row: int) -> None:
        self._detail_card.set_row(row)
        self._spirits_card.set_row(row)
        self._terrain_card.set_row(row)
        self._series_card.set_row(row)
        self._skills_card.set_row(row)
        self._upgraded_card.set_row(row)
