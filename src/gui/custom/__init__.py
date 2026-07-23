"""
GUI 自定义组件包

导出游戏枚举表、字段映射、字体常量和图标枚举，供 interface 和 widget 层使用。

Classes:
    EnumData: 游戏枚举数据（QObject，支持 self.tr）
    FieldMapping: 数据字段描述符
    CustomIcon: 自定义图标枚举

Constants:
    JP_FONT: 日文字体属性字典
    JP_QFONT: 日文字体 QFont 实例
    JP_FONT_STYLESHEET: 日文字体 QSS 片段
    EN_FONT: 西文字体属性字典
    EN_QFONT: 西文字体 QFont 实例
    EN_FONT_STYLESHEET: 西文字体 QSS 片段
"""

from .enums import EnumData
from .fields import FieldMapping
from .fonts import EN_FONT, EN_FONT_STYLESHEET, EN_QFONT, JP_FONT, JP_FONT_STYLESHEET, JP_QFONT
from .icon import CustomIcon
