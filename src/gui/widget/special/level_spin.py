"""
精神等级微调框 - 简化版 NumberSpin

提供数值步进功能，用于编辑精神指令的习得等级。
0 值显示为 "－"，发射信号时映射为 0xFF（255）。
支持键盘输入编辑。

Classes:
    LevelSpin: 精神等级微调框
"""

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QWidget

from gui.widget.abstract import VerticalSpinBox

_EMPTY_CHAR = "－"
_EMPTY_VALUE = 0xFF  # 值为 0 时发射此数值


class _LevelSpinBox(VerticalSpinBox):
    """内部微调框 — 0 值显示为 "－" """

    def textFromValue(self, value: int) -> str:
        """数值 → 显示文本，0 显示为 "－" """
        if value == 0:
            return _EMPTY_CHAR
        return str(value)

    def valueFromText(self, text: str) -> int:
        """显示文本 → 数值，"－" 视为 0"""
        if text.strip() == _EMPTY_CHAR:
            return 0
        try:
            return int(text)
        except ValueError:
            return 0


class LevelSpin(QWidget):
    """精神等级微调框 - 数值步进，编辑后发射 valueChanged

    0 值显示 "－"，实际发送的信号值为 0xFF（255）。
    """

    valueChanged = Signal(int)

    def __init__(self, parent=None):
        """初始化精神等级微调框

        Args:
            parent: 父 QWidget
        """
        super().__init__(parent)

        self._spin = _LevelSpinBox(self, editable=True)
        self._spin.setRange(0, 99)
        self._spin.valueChanged.connect(self._on_value_changed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._spin)

    # ========== 数据接口 ==========

    def set_value(self, value: int) -> None:
        """设置当前值

        Args:
            value: 等级数值，0xFF 显示为 "－"
        """
        self._spin.blockSignals(True)
        self._spin.setValue(0 if value == _EMPTY_VALUE else value)
        self._spin.blockSignals(False)

    def data_value(self) -> int:
        """获取当前值（已映射）

        Returns:
            当前值，0 时返回 0xFF
        """
        v = self._spin.value()
        return _EMPTY_VALUE if v == 0 else v

    # ========== 字体 ==========

    def apply_font(self, font: QFont | dict) -> None:
        """设置微调框字体

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

    def resetUI(self) -> None:
        """从全局配置刷新字体"""
        self._spin.resetUI()

    # ========== 内部槽 ==========

    def _on_value_changed(self, value: int) -> None:
        """值改变时发射映射后的 valueChanged"""
        self.valueChanged.emit(_EMPTY_VALUE if value == 0 else value)
