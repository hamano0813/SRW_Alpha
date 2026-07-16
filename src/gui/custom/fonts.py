"""
字体常量定义

提供全局字体配置字典，供表格模型 FontRole 查询使用。

Constants:
    TEXT_FONT: 默认表格正文样式（Yu Gothic UI, 14px, Normal）
"""

from PySide6.QtGui import QFont

TEXT_FONT = {
    "family": "Yu Gothic UI",
    "size": 14,
    "weight": QFont.Weight.Normal,
    "italic": False,
}
