"""
驾驶员侧边栏面板 - 分组卡片布局与数据编辑

提供驾驶员数据的编辑功能。各类卡片拆分为独立子类。
PilotPanel 只负责编排和接口转发。

Classes:
    PilotDetailCard:   驾驶员详细信息卡片（占位）
    SpiritsCard:       精神指令卡片
    TerrainCard:       地形适性卡片
    SeriesCard:        系列卡片
    SpecialSkillsCard: 特殊技能卡片（占位）
    UpgradedSkillsCard:等级制技能卡片（占位）
    PilotPanel:        驾驶员侧边栏面板
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QVBoxLayout
from qfluentwidgets import setFont

from gui.custom.enums import EnumData
from gui.widget import (
    BaseTableModel,
    CommonBitList,
    CardHeader,
    CommonMappingSpin,
    ProxyFrame,
    SpiritsEditor,
    CommonStretchLabel,
)


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


class SpiritsCard(CardHeader):
    """精神指令卡片 - 精神组合与习得等级编辑"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Spirits"))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self._spirits_editor = SpiritsEditor(self)
        self._spirits_editor.spiritChanged.connect(self._on_spirit_changed)
        self._spirits_editor.levelChanged.connect(self._on_level_changed)
        self.viewLayout.addWidget(self._spirits_editor)

    def set_row(self, row: int) -> None:
        super().set_row(row)
        spi_list = self._read("spi") or [0] * 6
        spl_list = self._read("spl") or [0] * 6
        for i in range(6):
            self._spirits_editor.set_spirit(i, int(spi_list[i]) if i < len(spi_list) else 0)
            self._spirits_editor.set_level(i, int(spl_list[i]) if i < len(spl_list) else 0)

    def _on_spirit_changed(self, idx: int, value: int) -> None:
        if self._model is not None and self._row >= 0:
            row_data = self._model.get_row_data(self._row)
            spi_list = row_data.get("spi", [0] * 6)
            if idx < len(spi_list):
                spi_list[idx] = value
        self.panelDataChanged.emit("spi")

    def _on_level_changed(self, idx: int, value: int) -> None:
        if self._model is not None and self._row >= 0:
            row_data = self._model.get_row_data(self._row)
            spl_list = row_data.get("spl", [0] * 6)
            if idx < len(spl_list):
                spl_list[idx] = value
        self.panelDataChanged.emit("spl")

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


class SeriesCard(CardHeader):
    """系列卡片 - Bit 位多选换乘系列列表"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Series"))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self._series_list = CommonBitList(parent=self)
        self._series_list.valueChanged.connect(lambda v: self._write("series", v))

        self.viewLayout.setContentsMargins(3, 8, 3, 8)
        self.viewLayout.addWidget(self._series_list)

    def set_row(self, row: int) -> None:
        super().set_row(row)
        self._series_list.set_value(self._read("series"))

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
