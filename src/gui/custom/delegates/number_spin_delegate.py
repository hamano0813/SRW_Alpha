"""
数值列委托 - 配合 NumberSpinBox 使用

每列一个委托实例，通过 setItemDelegateForColumn 绑定。
与 SingleLineDelegate 类似，但编辑器仅接受数值输入并右对齐。

Classes:
    NumberSpinDelegate: 数值列委托
"""

from typing import Any

from PySide6.QtCore import QModelIndex
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QStyleOptionViewItem, QWidget

from gui.custom.widgets import NumberSpinBox

from .base_delegate import DataWidgetDelegate


class NumberSpinDelegate(DataWidgetDelegate):
    """数值列委托 - 编辑器为 NumberSpinBox"""

    widget_class = NumberSpinBox

    def __init__(self, value_range: tuple[int, int] | None = None, show_sign: bool = False, show_buttons: bool = True, font: QFont | dict | None = None, parent=None):
        """初始化数值列委托

        Args:
            value_range: (最小值, 最大值)，None 表示无限制
            show_sign: 是否强制显示正号
            show_buttons: 是否显示左右微调按钮
            font: 编辑器字体，QFont 实例或字体属性字典
            parent: 父对象
        """
        super().__init__(parent=parent, font=font)
        self._value_range: tuple[int, int] | None = value_range
        self._show_sign = show_sign
        self._show_buttons = show_buttons

    def createEditor(self, parent, option, index) -> Any:
        """创建 NumberSpinBox 并注入取值范围

        Args:
            parent: 编辑器父控件
            option: 样式选项
            index: 单元格索引

        Returns:
            NumberSpinBox 实例
        """
        editor = NumberSpinBox(self._value_range, self._show_sign, self._show_buttons, parent)
        if self._font is not None:
            editor.apply_font(self._font)
        return editor

    # ========== 编辑器几何 ==========

    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """将编辑器位置设为单元格区域，上下清零

        有按钮时留出左侧间隙，无按钮时扩大编辑区域。

        Args:
            editor: NumberSpinBox 实例
            option: 样式选项
            index: 单元格索引
        """
        if self._show_buttons:
            rect = option.rect.adjusted(2, 0, 0, 0)
        else:
            rect = option.rect.adjusted(0, 0, -15, 0)
        editor.setGeometry(rect)
        editor.setFixedHeight(rect.height())

    # ========== 格式化 ==========

    def format_display(self, value) -> str:
        """将原始值格式化为数值文本

        Args:
            value: 原始值

        Returns:
            数值字符串（show_sign 时正值带 "+" 前缀）
        """
        if value is None:
            return ""
        try:
            v = int(value)
            if self._show_sign and v >= 0:
                return f"+{v}"
            return str(v)
        except (ValueError, TypeError):
            return str(value)

    def parse_display(self, text: str) -> Any:
        """将显示文本解析为数值

        自动去除 "+" 前缀。

        Args:
            text: 数字字符串

        Returns:
            整数值
        """
        try:
            return int(text.lstrip("+"))
        except (ValueError, TypeError):
            return 0
