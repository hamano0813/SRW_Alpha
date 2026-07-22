"""
数值微调框 - 在指定范围内步进

内嵌 VerticalSpinBox，使用 FluentIcon 箭头直接步进，无 flyout。
纯信号槽收发，不感知 model。

Classes:
    NumberSpin: 数值微调框
"""

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QVBoxLayout, QWidget

from .spin_box import VerticalSpinBox


class NumberSpin(QWidget):
    """数值微调框 - 在 [min, max] 范围内步进

    编辑后发射 valueChanged(int)，外部通过 set_value 控制显示。
    """

    valueChanged = Signal(int)

    def __init__(self, value_range: tuple[int, int] | None = None,
                 show_sign: bool = False, editable: bool = True, parent=None):
        """初始化数值微调框

        Args:
            value_range: (最小值, 最大值)，None 默认 (0, 9999)
            show_sign:   是否强制显示正号
            editable:    是否允许键盘输入
            parent:      父 QWidget
        """
        super().__init__(parent)

        min_val, max_val = value_range or (0, 9999)

        # ========== 内嵌微调框 ==========

        self._spin = _ProxySpin(min_val, max_val, show_sign, editable, self)
        self._spin.setRange(min_val, max_val)
        self._spin.valueChanged.connect(self.valueChanged)

        # ========== 布局 ==========

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._spin)

    # ========== 数据接口 ==========

    def set_value(self, value: int) -> None:
        """设置当前值并刷新显示"""
        self._spin.blockSignals(True)
        self._spin.setValue(int(value))
        self._spin.blockSignals(False)

    def value(self) -> int:
        """获取当前值"""
        return self._spin.value()

    # ========== 取值范围 ==========

    def set_range(self, min_val: int, max_val: int) -> None:
        """更新取值范围"""
        self._spin.setRange(min_val, max_val)

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


class _ProxySpin(VerticalSpinBox):
    """数值步进微调框 - 代理 VerticalSpinBox，添加符号显示"""

    def __init__(self, min_val: int, max_val: int, show_sign: bool, editable: bool, parent=None):
        super().__init__(parent, editable=editable)
        self._show_sign = show_sign

    def textFromValue(self, value: int) -> str:
        """数值 → 显示文本，show_sign 时正值显示 +N"""
        if self._show_sign and value >= 0:
            return f"+{value}"
        return str(value)
