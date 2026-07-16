"""
选项设置框架模块

提供应用程序的设置界面，包含界面设置和 ROM 设置两个主要分组。
管理主题、语言、字体、DPI 缩放等各种配置选项。

Classes:
    OptionFrame: 选项设置框架 - 管理所有应用程序设置
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QLayoutItem, QSpacerItem, QVBoxLayout, QWidget
from qfluentwidgets import (
    ComboBoxSettingCard,
    MessageBox,
    OptionsSettingCard,
    ScrollArea,
    SettingCardGroup,
    Theme,
    setFont,
    setTheme,
    setThemeColor,
)

import config
import utils
from gui.custom import CustomIcon

from . import ColorCard, FontCard, LanguageCard, RomCard


class OptionFrame(QFrame):
    """选项设置框架 - 管理所有应用程序设置"""

    themeChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("OptionFrame")

        self._interface_scaling_adjuest_to = self.tr("Interface scaling adjusted to")
        self._scaling_will_take_effect_after_restarting = self.tr("Scaling will take effect after restarting the interface")
        self._restart_now = self.tr("Restart Now")
        self._restart_later = self.tr("Restart Later")

        self.sub_frame = QFrame()

        self.language = LanguageCard(
            config.option.language,
            CustomIcon.LANGUAGE,
            self.tr("Interface Language"),
            self.tr("Change the language of the interface"),
            ["English", "简体中文", "日本語"],
        )

        self.ffont = FontCard(CustomIcon.FONT)
        self.theme = OptionsSettingCard(
            config.option.themeMode,
            CustomIcon.THEME,
            self.tr("Theme Mode"),
            self.tr("Change the theme mode of the interface"),
            texts=[self.tr("Light"), self.tr("Dark"), self.tr("Follow System")],
        )
        self.color = ColorCard(
            config.option.themeColor, CustomIcon.COLOR, self.tr("Theme Color"), self.tr("Change the theme color of the interface")
        )
        self.dpi = ComboBoxSettingCard(
            config.option.dpi,
            CustomIcon.ZOOM,
            self.tr("Interface Scaling"),
            self.tr("Change the scaling ratio of the interface"),
            ["100%", "125%", "150%", "175%", "200%"],
        )
        self.ui_group = self.create_group(self.tr("Interface Settings"), [self.language, self.ffont, self.theme, self.color, self.dpi])

        self.rom_card = RomCard(CustomIcon.ROM)
        self.rom_group = self.create_group(self.tr("ROM Settings"), [self.rom_card])

        sub_layout = QVBoxLayout()
        sub_layout.addWidget(self.rom_group)
        sub_layout.addWidget(self.ui_group)
        sub_layout.addStretch(10)

        self.sub_frame.setLayout(sub_layout)

        self.scroll_area = ScrollArea(self)
        self.scroll_area.setWidget(self.sub_frame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.enableTransparentBackground()

        layout = QVBoxLayout(self)
        layout.addWidget(self.scroll_area)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        config.option.themeColorChanged.connect(setThemeColor)
        config.option.themeChanged.connect(self.theme_changed)
        config.option.dpi.valueChanged.connect(self.dpi_changed)
        config.option.language.valueChanged.connect(self.language_changed)
        self.ffont.familyChanged.connect(self.window().resetUI)  # type: ignore

    def create_group(self, title: str, widgets: list[QWidget] = list()):
        """创建设置卡片组并初始化布局"""
        group = SettingCardGroup(title, self)
        setFont(group.titleLabel, 16)
        group.titleLabel.setIndent(6)

        spacer: QSpacerItem | QLayoutItem = group.vBoxLayout.itemAt(1)
        if isinstance(spacer, QSpacerItem):
            spacer.changeSize(0, 5)

        if widgets:
            for widget in widgets:
                group.addSettingCard(widget)
        return group

    def theme_changed(self, theme: Theme):
        """主题模式改变时更新全局主题"""
        setTheme(theme)
        self.themeChanged.emit()

    def dpi_changed(self, dpi: float):
        """DPI 缩放改变时显示重启提示对话框"""
        config.qconfig.save()
        scale = int(dpi * 100)

        w = MessageBox(
            self._interface_scaling_adjuest_to + f"{scale}%",
            self._scaling_will_take_effect_after_restarting,
            self.window(),
        )
        w.yesButton.setText(self._restart_now)
        w.cancelButton.setText(self._restart_later)

        if w.exec():
            utils.restart()

    def language_changed(self, _: str):
        """语言改变时刷新界面翻译和样式"""
        self.window().translateUI()  # type: ignore
        self.window().resetUI()  # type: ignore

    def resetUI(self):
        """重置所有设置组的字体"""
        setFont(self.rom_group.titleLabel, 16)
        setFont(self.ui_group.titleLabel, 16)
        self.ffont.resetUI()

    def translateUI(self):
        """更新所有界面文本的翻译"""
        self.rom_group.titleLabel.setText(self.tr("ROM Settings"))
        self.ui_group.titleLabel.setText(self.tr("Interface Settings"))

        self.language.titleLabel.setText(self.tr("Interface Language"))
        self.language.contentLabel.setText(self.tr("Change the language of the interface"))
        self.theme.card.titleLabel.setText(self.tr("Theme Mode"))
        self.theme.card.contentLabel.setText(self.tr("Change the theme mode of the interface"))

        self.theme.buttonGroup.buttons()[0].setText(self.tr("Light"))
        self.theme.buttonGroup.buttons()[1].setText(self.tr("Dark"))
        self.theme.buttonGroup.buttons()[2].setText(self.tr("Follow System"))
        self.theme.choiceLabel.setText(self.theme.buttonGroup.checkedButton().text())

        self.dpi.titleLabel.setText(self.tr("Interface Scaling"))
        self.dpi.contentLabel.setText(self.tr("Change the scaling ratio of the interface"))

        self._interface_scaling_adjuest_to = self.tr("Interface scaling adjusted to")
        self._scaling_will_take_effect_after_restarting = self.tr("Scaling will take effect after restarting the interface")
        self._restart_now = self.tr("Restart Now")
        self._restart_later = self.tr("Restart Later")

        self.color.translateUI()
        self.rom_card.translateUI()
        self.ffont.translateUI()
