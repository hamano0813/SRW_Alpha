"""
单元格委托模块

遵循按列分别设置委托（setItemDelegateForColumn）的设计，
每个 Delegate 对应一个 TableEditor 子类。

Classes:
    DataWidgetDelegate: 委托基类
    SingleLineDelegate: 单行文本列委托
    MultiLineDelegate: 多行文本列委托
    NumberSpinDelegate: 数值列委托
    MappingSpinDelegate: 数值微调列委托
"""

from .base_delegate import DataWidgetDelegate
from .mapping_spin_delegate import MappingSpinDelegate
from .multiline_delegate import MultiLineDelegate
from .number_spin_delegate import NumberSpinDelegate
from .single_line_delegate import SingleLineDelegate

__all__ = [
    "DataWidgetDelegate",
    "SingleLineDelegate",
    "MultiLineDelegate",
    "NumberSpinDelegate",
    "MappingSpinDelegate",
]
