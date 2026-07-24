"""
精神等级微调框 - 继承 VerticalSpinBox

0 值显示为 "－"，编辑后发射 valueChanged(int)，
其中 0 值发射 0xFF（255），与数据格式一致。

Classes:
    LevelSpin: 精神等级微调框
"""

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont

from gui.widget.abstract import VerticalSpinBox

_EMPTY_CHAR = "－"
_EMPTY_VALUE = 0xFF


class LevelSpin(VerticalSpinBox):
    """精神等级微调框 - 范围 0~99，0 显示 "－"，数据值为 0xFF"""

    _valueChanged = Signal(int)  # 内部信号，避免与 QSpinBox::valueChanged 重名

    def __init__(self, parent=None):
        super().__init__(parent, editable=True)
        self.setRange(0, 99)
        super().valueChanged.connect(self._on_value_changed)

    # ========== 显示映射 ==========

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

    # ========== 数据接口（0 ↔ 0xFF 映射） ==========

    def set_value(self, value: int) -> None:
        """设置当前值，0xFF 显示为 "－" """
        self.blockSignals(True)
        self.setValue(0 if value == _EMPTY_VALUE else value)
        self.blockSignals(False)

    def value(self) -> int:
        """获取当前数据值，显示 0 时返回 0xFF"""
        v = super().value()
        return _EMPTY_VALUE if v == 0 else v

    # ========== 对外信号代理 ==========

    @property
    def valueChanged(self):
        """向外暴露内部信号（与 SpiritsEditor 等外部连接兼容）"""
        return self._valueChanged

    # ========== 字体 ==========

    def apply_font(self, font: QFont | dict) -> None:
        """设置微调框字体"""
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
        self.setFont(font)

    # ========== 内部槽 ==========

    def _on_value_changed(self, spin_value: int) -> None:
        """spin 值改变时发射数据格式的 valueChanged"""
        self._valueChanged.emit(_EMPTY_VALUE if spin_value == 0 else spin_value)
