"""
数值微调列委托 - 配合 MapSpinWidget 使用

每列一个委托实例，通过 setItemDelegateForColumn 绑定。

Classes:
    MapSpinDelegate: 数值微调列委托
"""

from typing import Any

from PySide6.QtGui import QFont

from gui.custom.widgets import MapSpinWidget

from .base_delegate import DataWidgetDelegate


class MapSpinDelegate(DataWidgetDelegate):
    """数值微调列委托 - 编辑器为 MapSpinWidget"""

    widget_class = MapSpinWidget

    def __init__(self, mapping: dict[int, str] | None = None, font: QFont | dict | None = None, parent=None):
        """初始化数值微调列委托

        Args:
            mapping: {数值: 显示文本} 字典
            font: 编辑器字体
            parent: 父对象
        """
        super().__init__(parent=parent, font=font)
        self._value_mapping: dict[int, str] = mapping or {}

    def format_display(self, value) -> str:
        """将数值格式化为映射文本

        Args:
            value: 原始数值

        Returns:
            映射后的显示文本
        """
        if value is None:
            return ""
        try:
            return self._value_mapping.get(int(value), str(value))
        except (TypeError, ValueError):
            return str(value)

    def parse_display(self, text: str) -> Any:
        """将显示文本解析为数值

        Args:
            text: 显示文本

        Returns:
            对应数值，未找到时返回首个映射值
        """
        for k, v in self._value_mapping.items():
            if v == text:
                return k
        if self._value_mapping:
            return next(iter(self._value_mapping))
        return 0

    def updateEditorGeometry(self, editor, option, index) -> None:
        """微调编辑器几何，右扩 1px 使文字视觉居中"""
        rect = option.rect.adjusted(1, 0, 0, 0)
        editor.setGeometry(rect)
        editor.setFixedHeight(rect.height())

    def createEditor(self, parent, option, index) -> Any:
        """创建 MapSpinWidget 并注入映射表

        Args:
            parent: 编辑器父控件
            option: 样式选项
            index: 单元格索引

        Returns:
            MapSpinWidget 实例
        """
        editor = MapSpinWidget(self._value_mapping, parent)
        if self._font is not None:
            editor.apply_font(self._font)
        return editor
