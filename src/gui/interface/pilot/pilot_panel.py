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

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QVBoxLayout
from qfluentwidgets import setFont

from gui.custom.enums import EnumData
from gui.custom.models import BaseTableModel
from gui.custom.special import SpiritsEditor
from gui.custom.widgets import BitCheckList, MappingCompSpin
from gui.custom.widgets.stretch_label import StretchLabel
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
    """精神指令卡片 - 精神组合与习得等级编辑"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Spirits"))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self._spirits_editor = SpiritsEditor(self)
        self._spirits_editor.panelDataChanged.connect(self.panelDataChanged)
        self.viewLayout.addWidget(self._spirits_editor)

    def set_model(self, model: BaseTableModel) -> None:
        self._spirits_editor.set_model(model)

    def set_row(self, row: int) -> None:
        self._spirits_editor.set_row(row)

    def translateUI(self) -> None:
        self.setTitle(self.tr("Spirits"))
        self._spirits_editor.translateUI()

    def resetUI(self) -> None:
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
        self._spirits_editor.resetUI()


class TerrainCard(CardHeader):
    """地形适性卡片 - 四项地形适性横排"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Terrain"))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        _align = Qt.AlignmentFlag.AlignCenter
        _adapt = EnumData().PILOT["ADAPT"]

        self._air_label = StretchLabel(self.tr("Air"), self)
        self._air_label.setFixedWidth(60)
        self._air_spin = MappingCompSpin("air", mapping=_adapt, parent=self)
        self._air_spin.dataChanged.connect(self.panelDataChanged)

        self._grd_label = StretchLabel(self.tr("Lnd"), self)
        self._grd_label.setFixedWidth(60)
        self._grd_spin = MappingCompSpin("grd", mapping=_adapt, parent=self)
        self._grd_spin.dataChanged.connect(self.panelDataChanged)

        self._wtr_label = StretchLabel(self.tr("Sea"), self)
        self._wtr_label.setFixedWidth(60)
        self._wtr_spin = MappingCompSpin("wtr", mapping=_adapt, parent=self)
        self._wtr_spin.dataChanged.connect(self.panelDataChanged)

        self._spc_label = StretchLabel(self.tr("Spc"), self)
        self._spc_label.setFixedWidth(60)
        self._spc_spin = MappingCompSpin("spc", mapping=_adapt, parent=self)
        self._spc_spin.dataChanged.connect(self.panelDataChanged)

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

    def set_model(self, model: BaseTableModel) -> None:
        self._air_spin.set_model(model)
        self._grd_spin.set_model(model)
        self._wtr_spin.set_model(model)
        self._spc_spin.set_model(model)

    def set_row(self, row: int) -> None:
        self._air_spin.set_row(row)
        self._grd_spin.set_row(row)
        self._wtr_spin.set_row(row)
        self._spc_spin.set_row(row)

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


class SeriesCard(CardHeader):
    """系列卡片 - Bit 位多选换乘系列列表"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Series"))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self._series_list = BitCheckList("series", parent=self)
        self._series_list.dataChanged.connect(self.panelDataChanged)

        self.viewLayout.setContentsMargins(3, 8, 3, 8)
        self.viewLayout.addWidget(self._series_list)

    def set_model(self, model: BaseTableModel) -> None:
        self._series_list.set_model(model)

    def set_row(self, row: int) -> None:
        self._series_list.set_row(row)

    def translateUI(self) -> None:
        self.setTitle(self.tr("Series"))
        self._series_list.set_values(EnumData().PILOT["SERIES"])

    def resetUI(self) -> None:
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
        self._series_list.resetUI()


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
