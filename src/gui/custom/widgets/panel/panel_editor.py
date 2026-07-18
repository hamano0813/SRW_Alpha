"""
面板编辑器基类 - 操作整个数据字典

PanelEditor 与 TableEditor 不同：
  TableEditor 操作单个值（set_value / get_value），
  PanelEditor 通过 field 键操作整个数据字典。

子类嵌入具体控件（SearchLineEdit、ComboBox 等），
通过 set_data / get_data 完成外部与子类的数据交换。
放置于 widgets/panel/ 子包，供面板编辑器使用。

Classes:
    PanelEditor: 面板编辑器基类
"""

from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget


class PanelEditor(QWidget):
    """面板编辑器基类 - 通过 field 键操作字典

    set_data 存入整个字典后根据 field 提取对应值刷新控件，
    编辑后通过 _emit_data_changed 自动写回字典并发射信号。
    apply_font 设置字体，子类有内嵌控件时重写。

    Signals:
        dataChanged: 编辑确认后发射，携带当前数据字典
    """

    dataChanged = Signal(str)

    def __init__(self, field: str = "", parent=None):
        """初始化面板编辑器

        Args:
            field: 数据字典中对应的键名
            parent: 父 QWidget
        """
        super().__init__(parent)
        self._field: str = field
        self._data: dict | None = None
        self._value: Any = None

    # ========== 数据读写 ==========

    def set_data(self, data: dict | None) -> None:
        """存入整个数据字典并刷新显示

        从 data 中提取 self._field 对应的值用于子类控件显示。
        子类重写 format_value() 实现具体控件的刷新逻辑。

        Args:
            data: 数据字典，None 表示无数据
        """
        self._data = data
        self._value = data.get(self._field) if data is not None else None
        self.format_value()

    def get_data(self) -> dict | None:
        """返回当前数据字典

        Returns:
            数据字典，可能为 None
        """
        return self._data

    def get_value(self) -> Any:
        """返回 field 对应的当前值

        Returns:
            当前值，类型由子类定义
        """
        return self._value

    def _emit_data_changed(self) -> None:
        """将当前值写回字典并发射 dataChanged 信号

        子类在编辑确认后调用此方法。
        self._value 已为最新值，直接写回 self._data[self._field]。
        """
        if self._data is not None:
            self._data[self._field] = self._value
        self.dataChanged.emit(self._field)

    # ========== 子类扩展点 ==========

    def format_value(self) -> None:
        """按格式规则刷新控件显示

        基类为空，子类重写。
        set_data 末尾自动调用。
        """
        pass

    # ========== 字体 ==========

    def apply_font(self, font: QFont | dict) -> None:
        """设置编辑器字体

        基类调用 setFont，子类如有内嵌控件需重写以确保字体生效。

        Args:
            font: QFont 实例或字体属性字典（含 family/size/weight/italic 键）
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
        self.setFont(font)
