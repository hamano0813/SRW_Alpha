"""
MappingCompSpin 映射微调框 - 数值与文本映射单选

通过 mapping 字典实现 数值 ↔ 显示文本 的转换。
步进时仅在 mapping 的有效 key 范围内循环。
内嵌 qfluentwidgets CompactSpinBox，复用完整样式。

放置于 widgets/panel/ 子包，供面板编辑器使用。

Classes:
    MappingCompSpin: 映射微调框
"""

from typing import Any

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QVBoxLayout
from qfluentwidgets import CompactSpinBox

from .panel_editor import PanelEditor


class MappingCompSpin(PanelEditor):
    """映射微调框 - 数值与文本映射单选

    步进仅在 mapping 的有效 key 范围内循环。
    显示文本为 mapping 中对应的值。
    """

    def __init__(self, field: str, mapping: dict[int, str] | None = None, parent=None):
        """初始化映射微调框

        Args:
            field:   数据字典中对应的键名
            mapping: {数值: 显示文本} 字典
            parent:  父 QWidget
        """
        super().__init__(field, parent)

        self._map_mapping: dict[int, str] = mapping or {}
        self._sorted_keys: list[int] = sorted(self._map_mapping.keys())

        # ========== 内嵌 CompactSpinBox ==========

        self._spin = _ProxySpin(self._map_mapping, self._sorted_keys, self)
        if self._sorted_keys:
            self._spin.setRange(self._sorted_keys[0], self._sorted_keys[-1])
        self._spin.valueChanged.connect(self._on_value_changed)

        # ========== 布局 ==========

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._spin)

    # ========== 映射接口 ==========

    def set_mapping(self, mapping: dict[int, str]) -> None:
        """更新映射表并调整范围

        Args:
            mapping: {数值: 显示文本} 字典
        """
        self._map_mapping = mapping
        self._sorted_keys = sorted(self._map_mapping.keys())
        if self._sorted_keys:
            self._spin.setRange(self._sorted_keys[0], self._sorted_keys[-1])
        self._spin.set_mapping(mapping, self._sorted_keys)

    # ========== PanelEditor 数据协议 ==========

    def set_row(self, row: int) -> None:
        """切换行并刷新控件"""
        super().set_row(row)
        self._spin.blockSignals(True)
        if self._value is not None:
            self._spin.setValue(int(self._value))
        self._spin.blockSignals(False)

    def format_value(self) -> None:
        """刷新显示"""
        self._spin.blockSignals(True)
        if self._value is not None:
            self._spin.setValue(int(self._value))
        self._spin.blockSignals(False)

    def apply_font(self, font: QFont | dict) -> None:
        """设置编辑器字体

        Args:
            font: QFont 实例或字体属性字典
        """
        if isinstance(font, dict):
            qfont = QFont()
            family = font.get("family")
            size = font.get("size")
            weight = font.get("weight")
            italic = font.get("italic")
            if family:
                qfont.setFamily(family)
            if size:
                qfont.setPixelSize(size)
            if weight:
                qfont.setWeight(weight)
            if italic:
                qfont.setItalic(italic)
            font = qfont
        self._spin.setFont(font)

    # ========== 内部槽 ==========

    def _on_value_changed(self, value: int) -> None:
        """值改变时同步 _value 并写回字典"""
        self._value = value
        self._emit_data_changed()


class _ProxySpin(CompactSpinBox):
    """映射步进微调框 - 代理 CompactSpinBox 的 textFromValue / stepBy"""

    def __init__(self, mapping: dict[int, str], sorted_keys: list[int], parent=None):
        super().__init__(parent)
        self._map_mapping = mapping
        self._sorted_keys = sorted_keys

    def set_mapping(self, mapping: dict[int, str], sorted_keys: list[int]):
        self._map_mapping = mapping
        self._sorted_keys = sorted_keys

    def textFromValue(self, value: int) -> str:
        return self._map_mapping.get(value, str(value))

    def valueFromText(self, text: str) -> int:
        for k, v in self._map_mapping.items():
            if v == text:
                return k
        return self.value()

    def stepBy(self, steps: int) -> None:
        if not self._sorted_keys:
            super().stepBy(steps)
            return
        current = self.value()
        try:
            idx = self._sorted_keys.index(current)
        except ValueError:
            idx = 0
        new_idx = max(0, min(len(self._sorted_keys) - 1, idx + steps))
        self.setValue(self._sorted_keys[new_idx])
