"""
数值微调编辑器 - DataWidget 子类

内嵌 MappingSpinBox，通过 mapping 实现字母显示 ↔ 数字值的转换，
步进在 mapping 有效范围内循环。

Classes:
    MapSpinWidget: 数值微调编辑器
"""

from typing import Any

from PySide6.QtGui import QFont

from .data_widget import DataWidget
from .mapping_spinbox import MappingSpinBox


class MapSpinWidget(DataWidget):
    """数值微调编辑器 — 显示映射文本，存储数值

    内嵌 MappingSpinBox，步进时在 mapping 的 key 范围内循环。
    不超出映射边界，不落入映射外值。
    """

    def __init__(self, mapping: dict[int, str] | None = None, parent=None):
        """初始化数值微调编辑器

        Args:
            mapping: {数值: 显示文本} 字典
            parent: 父 QWidget
        """
        super().__init__(parent)

        self._spinbox = MappingSpinBox(mapping)

        # 信号
        self._spinbox.valueChanged.connect(self._on_value_changed)

        # 布局
        from PySide6.QtWidgets import QVBoxLayout

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._spinbox)

    # ========== 映射 ==========

    def set_mapping(self, mapping: dict[int, str]) -> None:
        """更新映射表

        Args:
            mapping: {数值: 显示文本} 字典
        """
        self._spinbox.set_mapping(mapping)

    # ========== 数据读写 ==========

    def set_value(self, value) -> None:
        """存入数值并刷新显示

        Args:
            value: 整数数值，若为 None 则设为首个映射值
        """
        super().set_value(value)

    def get_value(self) -> int:
        """返回当前数值"""
        return self._value if self._value is not None else 0

    # ========== 格式化 ==========

    def format_value(self) -> None:
        """将 _value 同步到微调框"""
        self._spinbox.blockSignals(True)
        if self._value is not None:
            self._spinbox.setValue(int(self._value))
        self._spinbox.blockSignals(False)

    # ========== 字体 ==========

    def apply_font(self, font: QFont) -> None:
        """将字体应用到内部微调框

        Args:
            font: 要应用的 QFont
        """
        self._spinbox.setFont(font)

    # ========== 校验 ==========

    def validate(self, value) -> bool:
        """校验值是否为整数或可转为整数"""
        try:
            int(value)
            return True
        except (TypeError, ValueError):
            return False

    # ========== 显示文本 ==========

    def format_display(self, value) -> str:
        """将数值格式化为显示文本"""
        if value is None:
            return ""
        try:
            return self._spinbox.textFromValue(int(value))
        except Exception:
            return str(value)

    def parse_display(self, text: str) -> Any:
        """将显示文本解析为数值"""
        return self._spinbox.valueFromText(text)

    # ========== 内部槽 ==========

    def _on_value_changed(self, value: int) -> None:
        """微调框值改变时同步 _value 并发射 dataChanged"""
        self._value = value
        self.dataChanged.emit(self._value)
