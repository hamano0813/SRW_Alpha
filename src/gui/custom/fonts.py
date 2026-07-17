"""
字体常量定义

提供全局字体配置字典及预编译的 QSS 样式表，供表格模型 FontRole、
Widget setFont 和 qfluentwidgets setCustomStyleSheet 使用。

Constants:
    JP_FONT: 日文字体属性字典
    JP_FONT_STYLESHEET: 日文字体对应的 QSS 片段
"""

from PySide6.QtGui import QFont
from qfluentwidgets import fontStyleSheet

# ========== 日文字体 ==========

JP_FONT = {
    "family": "Yu Gothic UI",
    "size": 14,
    "weight": QFont.Weight.Normal,
    "italic": False,
}

# 预编译为 QFont 并生成 QSS
_jp_qfont = QFont(JP_FONT["family"])
_jp_qfont.setPixelSize(JP_FONT["size"])
_jp_qfont.setWeight(JP_FONT["weight"])
_jp_qfont.setItalic(JP_FONT["italic"])
JP_FONT_STYLESHEET = fontStyleSheet(_jp_qfont)
