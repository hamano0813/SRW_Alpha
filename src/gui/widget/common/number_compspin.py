"""
NumberCompSpin 数值微调框 - 在指定范围内步进

通过 value_range 定义 [min, max] 取值范围，支持可选的符号显示。
内嵌 VerticalSpinBox，使用 FluentIcon 箭头直接步进，无 flyout。

放置于 widgets/panel/ 子包，供面板编辑器使用。

Classes:
    NumberCompSpin: 数值微调框
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QVBoxLayout

from .panel_editor import PanelEditor
from .spin_box import VerticalSpinBox


class NumberCompSpin(PanelEditor):
    """数值微调框 - 在 [min, max] 范围内步进

    继承 PanelEditor，内嵌 VerticalSpinBox。
    支持运行时调整取值范围和可选的正号显示。
    """

    def __init__(self, field: str, value_range: tuple[int, int] | None = None,
                 show_sign: bool = False, editable: bool = True, parent=None):
        """初始化数值微调框

        Args:
            field: 数据字典中对应的键名
            value_range: (最小值, 最大值)，None 默认 (0, 9999)
            show_sign: 是否强制显示正号
            editable: 是否允许键盘输入
            parent: 父 QWidget
        """
        super().__init__(field, parent)

        min_val, max_val = value_range or (0, 9999)

        # ========== 内嵌微调框 ==========

        self._spin = _ProxySpin(min_val, max_val, show_sign, editable, self)
        self._spin.setRange(min_val, max_val)
        self._spin.valueChanged.connect(self._on_value_changed)

        # ========== 布局 ==========

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._spin)

    # ========== 取值范围 ==========

    def set_range(self, min_val: int, max_val: int) -> None:
        """更新取值范围

        Args:
            min_val: 最小值
            max_val: 最大值
        """
        self._spin.setRange(min_val, max_val)

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

    # ========== 内部槽 ==========

    def _on_value_changed(self, value: int) -> None:
        """值改变时同步 _value 并写回字典"""
        self._value = value
        self._emit_data_changed()


class _ProxySpin(VerticalSpinBox):
    """数值步进微调框 - 代理 VerticalSpinBox，添加符号显示"""

    def __init__(self, min_val: int, max_val: int, show_sign: bool, editable: bool, parent=None):
        """初始化数值步进微调框

        Args:
            min_val: 最小值
            max_val: 最大值
            show_sign: 是否强制显示正号
            editable: 是否允许键盘输入
            parent: 父 QWidget
        """
        super().__init__(parent, editable=editable)
        self._show_sign = show_sign

    def textFromValue(self, value: int) -> str:
        """数值 → 显示文本，show_sign 时正值显示 +N"""
        if self._show_sign and value >= 0:
            return f"+{value}"
        return str(value)
