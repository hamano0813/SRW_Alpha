"""
自定义图标模块

定义应用程序中使用的所有自定义图标，支持主题自适应。
图标文件命名规则：{name}_{color}.svg，其中 color 为 dark 或 light。
使用 qfluentwidgets 的 FluentIconBase 实现主题色切换。

Classes:
    CustomIcon: 自定义图标枚举 - 支持主题自适应的 SVG 图标
"""

from enum import Enum

from qfluentwidgets import FluentIconBase, Theme, getIconColor

import res


class CustomIcon(FluentIconBase, Enum):
    """自定义图标枚举 - 支持主题自适应的 SVG 图标"""

    # 应用程序品牌
    LOGO = "icon/logo"
    SPLASH = "icon/splash"

    # 导航功能
    HOME = "icon/home"
    HELP = "icon/help"
    OPTION = "icon/option"

    # 界面设置
    LANGUAGE = "icon/language"
    FONT = "icon/font"
    THEME = "icon/theme"
    COLOR = "icon/color"
    ZOOM = "icon/zoom"

    # ROM 文件
    ROM = "icon/rom"

    def path(self, theme=Theme.AUTO):
        """
        根据当前主题返回对应的图标文件路径。

        图标文件命名格式：{name}_dark.svg 或 {name}_light.svg

        Args:
            theme: 主题模式，默认为自动检测

        Returns:
            str: 图标资源路径（如 :/icon/home_dark.svg）
        """
        return f":/{self.value}_{getIconColor(theme)}.svg"
