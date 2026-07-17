"""
单元格委托模块

遵循按列分别设置委托（setItemDelegateForColumn）的设计，
每个 Delegate 对应一个 DataWidget 子类。

Classes:
    DataWidgetDelegate: 委托基类
    LineTextDelegate: 单行文本列委托
    MapSpinDelegate: 数值微调列委托
"""

from .base_delegate import DataWidgetDelegate
from .line_text_delegate import LineTextDelegate
from .map_spin_delegate import MapSpinDelegate

__all__ = [
    "DataWidgetDelegate",
    "LineTextDelegate",
    "MapSpinDelegate",
]
