"""
单元格委托模块

遵循按列分别设置委托（setItemDelegateForColumn）的设计，
每个 Delegate 对应一个 DataWidget 子类。

Classes:
    DataWidgetDelegate: 委托基类
    LineTextFirstDelegate: 首列单行文本委托
    LineTextMidDelegate: 中间列单行文本委托
    LineTextLastDelegate: 末列单行文本委托
"""

from .base_delegate import DataWidgetDelegate
from .last_text_delegate import LineTextLastDelegate
from .line_text_delegate import LineTextFirstDelegate
from .line_text_mid_delegate import LineTextMidDelegate

__all__ = [
    "DataWidgetDelegate",
    "LineTextFirstDelegate",
    "LineTextMidDelegate",
    "LineTextLastDelegate",
]
