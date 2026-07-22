"""
映射微调框 - 数值与文本映射单选

通过 mapping 字典实现 数值 ↔ 显示文本 的转换。
步进时仅在 mapping 的有效 key 范围内循环。
内嵌 VerticalSpinBox，纯信号槽收发。

Classes:
    CommonMappingSpin: 映射微调框
"""

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QVBoxLayout, QWidget

from gui.widget.abstract import VerticalSpinBox


class CommonMappingSpin(QWidget):
    """映射微调框 - 数值与文本映射单选

    步进仅在 mapping 的有效 key 范围内循环。
    编辑后发射 valueChanged(int)，外部通过 set_value 控制显示。
    """

    valueChanged = Signal(int)

    def __init__(self, mapping: dict[int, str] | None = None, parent=None):
        """初始化映射微调框

        Args:
            mapping: {数值: 显示文本} 字典
            parent:  父 QWidget
        """
        super().__init__(parent)

        self._map_mapping: dict[int, str] = mapping or {}
        self._sorted_keys: list[int] = sorted(self._map_mapping.keys())
        self._current_value: int = 0

        # ========== 内嵌微调框 ==========

        self._spin = _ProxySpin(self._map_mapping, self._sorted_keys, self)
        if self._sorted_keys:
            self._spin.setRange(self._sorted_keys[0], self._sorted_keys[-1])
        self._spin.valueChanged.connect(self._on_value_changed)

        # ========== 布局 ==========

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._spin)

    # ========== 数据接口 ==========

    def set_value(self, value: int) -> None:
        """设置当前值并刷新显示"""
        self._current_value = value
        self._spin.blockSignals(True)
        self._spin.setValue(int(value))
        self._spin.blockSignals(False)
        self._adjust_zero_margin()

    def value(self) -> int:
        """获取当前值"""
        return self._current_value

    # ========== 映射接口 ==========

    def set_mapping(self, mapping: dict[int, str]) -> None:
        """更新映射表并调整范围（保持当前选中值）

        Args:
            mapping: {数值: 显示文本} 字典
        """
        old_value = self._current_value
        self._map_mapping = mapping
        self._sorted_keys = sorted(self._map_mapping.keys())
        if self._sorted_keys:
            self._spin.setRange(self._sorted_keys[0], self._sorted_keys[-1])
        self._spin.set_mapping(mapping, self._sorted_keys)
        # 恢复选中值
        if old_value in self._sorted_keys:
            self._spin.blockSignals(True)
            self._spin.setValue(old_value)
            self._spin.blockSignals(False)

    # ========== 字体 ==========

    def apply_font(self, font: QFont | dict) -> None:
        """设置编辑器字体"""
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

    def resetUI(self) -> None:
        """从全局配置刷新字体"""
        self._spin.resetUI()

    # ========== 内部槽 ==========

    def _adjust_zero_margin(self) -> None:
        """值为 0 时右缩进收窄 4px，使 '－' 符号视觉居中"""
        le = self._spin.lineEdit()
        if self._current_value == 0:
            le.setTextMargins(0, 0, 18, 0)
        else:
            le.setTextMargins(0, 0, 21, 0)

    def _on_value_changed(self, value: int) -> None:
        """值改变时更新内部状态并发射信号"""
        self._current_value = value
        self._adjust_zero_margin()
        self.valueChanged.emit(value)


class _ProxySpin(VerticalSpinBox):
    """映射步进微调框 - 代理 VerticalSpinBox 的 textFromValue / stepBy"""

    def __init__(self, mapping: dict[int, str], sorted_keys: list[int], parent=None):
        super().__init__(parent, editable=False)
        self._map_mapping = mapping
        self._sorted_keys = sorted_keys

    def set_mapping(self, mapping: dict[int, str], sorted_keys: list[int]) -> None:
        """更新映射表"""
        self._map_mapping = mapping
        self._sorted_keys = sorted_keys

    def textFromValue(self, value: int) -> str:
        """数值 → 显示文本"""
        return self._map_mapping.get(value, str(value))

    def valueFromText(self, text: str) -> int:
        """显示文本 → 数值"""
        for k, v in self._map_mapping.items():
            if v == text:
                return k
        return self.value()

    def stepBy(self, steps: int) -> None:
        """按映射键列表步进"""
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
