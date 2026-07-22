"""
表格内编辑器基类 - 解耦原始值与格式化显示

子类内嵌具体控件（QSpinBox / QComboBox / QLineEdit 等），
通过 set_value / get_value 完成外部与子类的数据交换。
放置于 widgets/table/ 子包，供 delegates 在表格编辑时实例化。

Classes:
    CellEditor: 表格内编辑器基类
"""

from typing import Any

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget


class CellEditor(QWidget):
    """表格内编辑器基类 - 解耦原始值与格式化显示

    set_value 存入原始值后自动调 format_value() 刷新控件显示，
    get_value 返回原始值供 Delegate 写回 model。
    is_valid 由子类重写，用于拒绝不可接受的值。
    format_display / parse_display 供表格 DisplayRole 和批量粘贴使用。

    Signals:
        dataChanged: 确认编辑后发射，携带当前值
    """

    dataChanged = Signal(object)

    def __init__(self, parent=None):
        """初始化数据编辑控件

        Args:
            parent: 父 QWidget
        """
        # 注意：不调 super().__init__，当与 QLineEdit/QSpinBox 等
        # 多重继承时，另一侧父类已初始化 QWidget，重复调用会崩溃。
        self._value: Any = None

    # ========== 数据读写 ==========

    def set_value(self, value) -> None:
        """存入原始值并刷新显示

        子类重写 format_value() 实现显示逻辑，
        基类仅做赋值和刷新。

        Args:
            value: 原始值（类型由子类定义）
        """
        self._value = value
        self.format_value()

    def get_value(self) -> Any:
        """返回当前原始值

        Returns:
            原始值，供 Delegate 写回 model
        """
        return self._value

    # ========== 子类扩展点 ==========

    def format_value(self) -> None:
        """按格式规则刷新控件显示

        基类为空，子类重写。
        set_value 末尾自动调用。
        """
        pass

    # ========== 字体 ==========

    def apply_font(self, font: QFont) -> None:
        """供 Delegate 设置编辑器字体

        基类调用 setFont，子类如有内嵌控件需重写以确保字体生效。

        Args:
            font: 要应用的 QFont
        """
        self.setFont(font)

    def is_valid(self, value) -> bool:
        """校验值是否可接受

        子类重写，返回 False 表示值不合法应拒绝写回。

        Args:
            value: 待校验的原始值

        Returns:
            True 可接受，False 拒绝
        """
        return True

    # ========== 显示文本 ==========

    def format_display(self, value) -> str:
        """将原始值格式化为表格 DisplayRole 显示文本

        子类可访问实例属性（如映射表）完成格式化。

        Args:
            value: 原始值

        Returns:
            显示文本
        """
        return str(value)

    def parse_display(self, text: str) -> Any:
        """将显示文本反向解析为原始值

        供批量粘贴（TSV → value）使用，子类按需重写。

        Args:
            text: 显示文本

        Raises:
            NotImplementedError: 子类未实现
        """
        raise NotImplementedError(f"{type(self).__name__} does not implement parse_display")
