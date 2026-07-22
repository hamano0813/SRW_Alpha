"""
精神指令编辑器 - 精神组合与习得等级编辑

两行六列布局，奇数列为精神指令下拉框，偶数列为习得等级微调框。
第一行：spi[0..2] / spl[0..2]，第二行：spi[3..5] / spl[3..5]。

使用 SpiritCombo 和 LevelSpin 作为子控件，由本模块统一管理数据收发和信号来回。

Classes:
    SpiritsEditor: 精神指令编辑器
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout

from .level_spin import LevelSpin
from .spirit_combo import SpiritCombo
from gui.custom.enums import EnumData
from gui.widget.table import BaseTableModel
from gui.widget.proxy import ProxyFrame


class SpiritsEditor(ProxyFrame):
    """精神指令编辑器 - 6 组精神 × 等级，2 行 6 列网格布局"""

    panelDataChanged = Signal(str)  # 字段名

    _SPI_FIELD = "spi"
    _SPL_FIELD = "spl"
    _SPIRIT_COUNT = 6

    def __init__(self, parent=None):
        """初始化精神指令编辑器

        Args:
            parent: 父 QWidget
        """
        super().__init__(parent)
        self._model: BaseTableModel | None = None
        self._row: int = -1

        # ========== 精神名称映射 ==========

        self._spirit_mapping: dict[int, str] = {}
        self._refresh_mapping()

        # ========== 6 组控件（spi + spl） ==========

        self._spi_combos: list[SpiritCombo] = []
        self._spl_spins: list[LevelSpin] = []

        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(4)

        for i in range(self._SPIRIT_COUNT):
            combo = SpiritCombo(self._spirit_mapping, self)
            combo.valueChanged.connect(lambda v, idx=i: self._on_spi_changed(idx, v))
            self._spi_combos.append(combo)

            spin = LevelSpin(parent=self)
            spin.valueChanged.connect(lambda v, idx=i: self._on_spl_changed(idx, v))
            self._spl_spins.append(spin)

            row = 0 if i < 3 else 1
            col = (i % 3) * 2
            grid.addWidget(combo, row, col)
            grid.addWidget(spin, row, col + 1)

        self.setLayout(grid)

    # ========== 映射刷新 ==========

    def _refresh_mapping(self) -> None:
        """从 EnumData().SPIRIT 重建 {数值: 显示文本} 映射"""
        self._spirit_mapping = dict(EnumData().SPIRIT)

    # ========== 数据接口 ==========

    def set_model(self, model: BaseTableModel) -> None:
        """注入数据模型

        Args:
            model: BaseTableModel 实例
        """
        self._model = model

    def set_row(self, row: int) -> None:
        """切换行并刷新所有子控件

        Args:
            row: 源模型行号
        """
        self._row = row
        if self._model is None or row < 0:
            return

        row_data = self._model.get_row_data(row)
        spi_list = row_data.get(self._SPI_FIELD, [0] * self._SPIRIT_COUNT)
        spl_list = row_data.get(self._SPL_FIELD, [0] * self._SPIRIT_COUNT)

        for i in range(self._SPIRIT_COUNT):
            self._spi_combos[i].set_value(int(spi_list[i]) if i < len(spi_list) else 0)
            self._spl_spins[i].set_value(int(spl_list[i]) if i < len(spl_list) else 0)

    # ========== 编辑回写 ==========

    def _on_spi_changed(self, idx: int, value: int) -> None:
        """精神指令变更时写回 model

        Args:
            idx:   列表索引 0..5
            value: 精神指令数值 key
        """
        if self._model is not None and self._row >= 0:
            row_data = self._model.get_row_data(self._row)
            spi_list = row_data.get(self._SPI_FIELD, [0] * self._SPIRIT_COUNT)
            if idx < len(spi_list):
                spi_list[idx] = value
        self.panelDataChanged.emit(self._SPI_FIELD)

    def _on_spl_changed(self, idx: int, value: int) -> None:
        """习得等级变更时写回 model

        Args:
            idx:   列表索引 0..5
            value: 等级数值
        """
        if self._model is not None and self._row >= 0:
            row_data = self._model.get_row_data(self._row)
            spl_list = row_data.get(self._SPL_FIELD, [0] * self._SPIRIT_COUNT)
            if idx < len(spl_list):
                spl_list[idx] = value
        self.panelDataChanged.emit(self._SPL_FIELD)

    # ========== 翻译与字体 ==========

    def translateUI(self) -> None:
        """刷新精神名称映射（语言切换后）"""
        self._refresh_mapping()
        for combo in self._spi_combos:
            combo.set_mapping(self._spirit_mapping)

    def resetUI(self) -> None:
        """刷新所有控件字体"""
        for combo in self._spi_combos:
            combo.resetUI()
        for spin in self._spl_spins:
            spin.resetUI()
        super().resetUI()
