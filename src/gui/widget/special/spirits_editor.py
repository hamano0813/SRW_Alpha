"""
精神指令编辑器 - 精神组合与习得等级编辑

两行六列布局，奇数列为精神指令下拉框，偶数列为习得等级微调框。
第一行：spi[0..2] / spl[0..2]，第二行：spi[3..5] / spl[3..5]。
纯布局容器，数据读写由卡片层负责。

Classes:
    SpiritsEditor: 精神指令编辑器
"""

from PySide6.QtCore import Signal

from gui.custom.enums import EnumData
from gui.widget.proxy import ProxyFrame
from .level_spin import LevelSpin
from .spirit_combo import SpiritCombo


class SpiritsEditor(ProxyFrame):
    """精神指令编辑器 - 6 组精神 × 等级，纯布局容器

    卡片层通过 set_spirit(idx, value) / set_level(idx, value) 写入显示，
    通过 spiritChanged(idx, value) / levelChanged(idx, value) 信号接收编辑回写。
    """

    spiritChanged = Signal(int, int)  # idx, value
    levelChanged = Signal(int, int)   # idx, value

    _SPIRIT_COUNT = 6

    def __init__(self, parent=None):
        super().__init__(parent)

        # ========== 精神名称映射 ==========

        self._spirit_mapping: dict[int, str] = {}
        self._refresh_mapping()

        # ========== 6 组控件（spi + spl） ==========

        self._spi_combos: list[SpiritCombo] = []
        self._spl_spins: list[LevelSpin] = []

        from PySide6.QtWidgets import QGridLayout
        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(4)

        for i in range(self._SPIRIT_COUNT):
            combo = SpiritCombo(self._spirit_mapping, self)
            combo.valueChanged.connect(lambda v, idx=i: self.spiritChanged.emit(idx, v))
            self._spi_combos.append(combo)

            spin = LevelSpin(parent=self)
            spin.valueChanged.connect(lambda v, idx=i: self.levelChanged.emit(idx, v))
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

    # ========== 数据接口（由卡片层调用） ==========

    def set_spirit(self, idx: int, value: int) -> None:
        """设置第 idx 位的精神指令值"""
        if idx < len(self._spi_combos):
            self._spi_combos[idx].set_value(value)

    def set_level(self, idx: int, value: int) -> None:
        """设置第 idx 位的习得等级"""
        if idx < len(self._spl_spins):
            self._spl_spins[idx].set_value(value)

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
