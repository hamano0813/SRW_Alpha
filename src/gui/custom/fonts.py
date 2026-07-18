"""
字体常量定义

提供全局字体配置字典及预编译的 QSS 样式表，供表格模型 FontRole、
Widget setFont 和 qfluentwidgets setCustomStyleSheet 使用。

Constants:
    JP_FONT: 日文字体属性字典
    JP_FONT_STYLESHEET: 日文字体对应的 QSS 片段
    JP_FONT: 日文字体属性字典
    JP_FONT_STYLESHEET: 日文字体对应的 QSS 片段
    EN_FONT: 西文字体（Consolas，全 Windows 语言版本可用）
    EN_FONT_STYLESHEET: 西文字体对应的 QSS 片段
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

# QFont 实例（供 apply_font 等处直接使用）
JP_QFONT = _jp_qfont

# ========== 西文字体 ==========

EN_FONT = {
    "family": "Segoe UI",
    "size": 14,
    "weight": QFont.Weight.DemiBold,
    "italic": False,
}

_en_qfont = QFont(EN_FONT["family"])
_en_qfont.setPixelSize(EN_FONT["size"])
_en_qfont.setWeight(EN_FONT["weight"])
_en_qfont.setItalic(EN_FONT["italic"])
EN_FONT_STYLESHEET = fontStyleSheet(_en_qfont)

# QFont 实例
EN_QFONT = _en_qfont
