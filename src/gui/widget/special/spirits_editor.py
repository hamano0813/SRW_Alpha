"""
精神指令卡片 - 精神组合与习得等级编辑

两行六列布局，奇数列为精神指令下拉框，偶数列为习得等级微调框。
第一行：spi[0..2] / spl[0..2]，第二行：spi[3..5] / spl[3..5]。
继承 CardHeader，自行读写 model 数据。

Classes:
    SpiritsEditor: 精神指令卡片
"""

from PySide6.QtWidgets import QGridLayout

from gui.custom import EnumData
from gui.widget.proxy import CardHeader
from .level_spin import LevelSpin
from .spirit_combo import SpiritCombo


class SpiritsEditor(CardHeader):
    """精神指令卡片 - 6 组精神 × 等级，网格布局"""

    _SPIRIT_COUNT = 6

    def __init__(self, parent=None):
        super().__init__(parent)
        self._spirit_mapping: dict[int, str] = {}
        self._refresh_mapping()

        self._spi_combos: list[SpiritCombo] = []
        self._spl_spins: list[LevelSpin] = []

        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(4)

        for i in range(self._SPIRIT_COUNT):
            combo = SpiritCombo(self._spirit_mapping, self)
            combo.valueChanged.connect(lambda v, idx=i: self._on_spirit(idx, v))
            self._spi_combos.append(combo)

            spin = LevelSpin(parent=self)
            spin.valueChanged.connect(lambda v, idx=i: self._on_level(idx, v))
            self._spl_spins.append(spin)

            row = 0 if i < 3 else 1
            col = (i % 3) * 2
            grid.addWidget(combo, row, col)
            grid.addWidget(spin, row, col + 1)

        self.viewLayout.addLayout(grid)

    # ========== 映射刷新 ==========

    def _refresh_mapping(self) -> None:
        self._spirit_mapping = dict(EnumData().SPIRIT)

    # ========== 数据接口 ==========

    def set_row(self, row: int) -> None:
        super().set_row(row)
        spi_list = self._read("spi") or [0] * self._SPIRIT_COUNT
        spl_list = self._read("spl") or [0] * self._SPIRIT_COUNT
        for i in range(self._SPIRIT_COUNT):
            self._spi_combos[i].set_value(int(spi_list[i]) if i < len(spi_list) else 0)
            self._spl_spins[i].set_value(int(spl_list[i]) if i < len(spl_list) else 0)

    def _on_spirit(self, idx: int, value: int) -> None:
        row_data = self._model.get_row_data(self._row) if self._model and self._row >= 0 else None
        if row_data is not None:
            spi_list = row_data.get("spi", [0] * self._SPIRIT_COUNT)
            if idx < len(spi_list):
                spi_list[idx] = value
        self.panelDataChanged.emit("spi")

    def _on_level(self, idx: int, value: int) -> None:
        row_data = self._model.get_row_data(self._row) if self._model and self._row >= 0 else None
        if row_data is not None:
            spl_list = row_data.get("spl", [0] * self._SPIRIT_COUNT)
            if idx < len(spl_list):
                spl_list[idx] = value
        self.panelDataChanged.emit("spl")

    # ========== 翻译与字体 ==========

    def translateUI(self) -> None:
        self._refresh_mapping()
        for combo in self._spi_combos:
            combo.set_mapping(self._spirit_mapping)

    def resetUI(self) -> None:
        for combo in self._spi_combos:
            combo.resetUI()
        for spin in self._spl_spins:
            spin.resetUI()
        super().resetUI()
