"""
自定义图标模块

定义应用程序中使用的所有自定义图标，支持主题自适应。
图标文件命名规则：{name}_{color}.svg，其中color为dark或light。
"""

from enum import Enum

from qfluentwidgets import FluentIconBase, Theme, getIconColor

import res


class CustomIcon(FluentIconBase, Enum):
    """自定义图标枚举 - 支持主题自适应的SVG图标"""

    # 应用程序品牌图标
    LOGO = "icon/logo"  # 应用程序Logo
    SPLASH = "icon/splash"  # 启动画面图标

    # 通用功能图标
    HELP = "icon/help"  # 帮助图标
    OPTION = "icon/option"  # 选项/设置图标

    # 界面设置图标
    LANGUAGE = "icon/language"  # 语言设置图标
    FONT = "icon/font"  # 字体设置图标
    THEME = "icon/theme"  # 主题模式图标
    COLOR = "icon/color"  # 主题颜色图标
    ZOOM = "icon/zoom"  # DPI缩放图标

    # ROM文件相关图标
    ROM = "icon/rom"  # ROM文件图标

    def path(self, theme=Theme.AUTO):
        """
        获取主题相关的图标路径

        根据当前主题返回对应的图标文件路径。
        图标文件命名格式：{name}_dark.svg 或 {name}_light.svg

        Args:
            theme: 主题模式，默认为自动检测

        Returns:
            str: 图标资源路径
        """
        return f":/{self.value}_{getIconColor(theme)}.svg"
