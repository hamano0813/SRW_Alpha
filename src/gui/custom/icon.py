from enum import Enum

from qfluentwidgets import FluentIconBase, Theme, getIconColor

import res


class CustomIcon(FluentIconBase, Enum):
    LOGO = "icon/logo"
    SPLASH = "icon/splash"

    HELP = "icon/help"
    OPTION = "icon/option"

    LANGUAGE = "icon/language"
    FONT = "icon/font"
    THEME = "icon/theme"
    COLOR = "icon/color"
    ZOOM = "icon/zoom"

    ROM = "icon/rom"

    def path(self, theme=Theme.AUTO):
        return f":/{self.value}_{getIconColor(theme)}.svg"
