"""
选项设置框架模块

提供应用程序的设置界面，包含界面设置和ROM设置两个主要分组。
管理主题、语言、字体、DPI缩放等各种配置选项。
"""

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
from core import utils
from gui.custom import CustomIcon

from . import ColorCard, FontCard, LanguageCard, RomCard


class OptionFrame(QFrame):
    """选项设置框架 - 管理所有应用程序设置"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("OptionFrame")

        # 初始化DPI缩放对话框的翻译文本
        self._interface_scaling_adjuest_to = self.tr("Interface scaling adjusted to")
        self._scaling_will_take_effect_after_restarting = self.tr("Scaling will take effect after restarting the interface")
        self._restart_now = self.tr("Restart Now")
        self._restart_later = self.tr("Restart Later")

        # 创建子框架容器
        self.sub_frame = QFrame()

        # 创建界面设置卡片组件
        self.language = LanguageCard(
            config.option.language,
            CustomIcon.LANGUAGE,
            self.tr("Interface Language"),
            self.tr("Change the language of the interface"),
            ["English", "简体中文", "日本語"],
        )

        self.ffont = FontCard(CustomIcon.FONT)  # 字体设置卡片
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
        # 创建界面设置组
        self.ui_group = self.create_group(self.tr("Interface Settings"), [self.language, self.ffont, self.theme, self.color, self.dpi])

        # 创建ROM设置组
        self.rom_card = RomCard(CustomIcon.ROM)
        self.rom_group = self.create_group(self.tr("Rom Settings"), [self.rom_card])

        # 设置子框架布局
        sub_layout = QVBoxLayout()
        sub_layout.addWidget(self.rom_group)  # ROM设置在上方
        sub_layout.addWidget(self.ui_group)  # 界面设置在下方
        sub_layout.addStretch(10)  # 底部弹性空间

        self.sub_frame.setLayout(sub_layout)

        # 创建滚动区域以支持内容溢出时的滚动
        self.scroll_area = ScrollArea(self)
        self.scroll_area.setWidget(self.sub_frame)
        self.scroll_area.setWidgetResizable(True)  # 自动调整内容大小
        self.scroll_area.enableTransparentBackground()  # 透明背景

        # 设置主框架布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.scroll_area)
        layout.setContentsMargins(0, 0, 0, 0)  # 无边距
        self.setLayout(layout)

        # 连接配置改变信号到对应的处理函数
        config.option.themeColorChanged.connect(setThemeColor)  # 主题颜色改变
        config.option.themeChanged.connect(self.theme_changed)  # 主题模式改变
        config.option.dpi.valueChanged.connect(self.dpi_changed)  # DPI缩放改变
        config.option.language.valueChanged.connect(self.language_changed)  # 语言改变
        self.ffont.familyChanged.connect(self.window().resetUI)  # type: ignore  # 字体改变时重置界面

    def create_group(self, title: str, widgets: list[QWidget] = list()):
        """创建设置卡片组"""
        group = SettingCardGroup(title, self)
        setFont(group.titleLabel, 16)  # 设置标题字体大小
        group.titleLabel.setIndent(6)  # 设置标题缩进

        # 调整组内间距
        spacer: QSpacerItem | QLayoutItem = group.vBoxLayout.itemAt(1)
        if isinstance(spacer, QSpacerItem):
            spacer.changeSize(0, 5)

        # 添加设置卡片到组中
        if widgets:
            for widget in widgets:
                group.addSettingCard(widget)
        return group

    def theme_changed(self, theme: Theme):
        """主题模式改变时的处理"""
        setTheme(theme)

    def dpi_changed(self, dpi: float):
        """DPI缩放改变时的处理 - 显示重启提示对话框"""
        config.qconfig.save()  # 保存配置
        scale = int(dpi * 100)

        # 创建重启提示对话框
        w = MessageBox(
            self._interface_scaling_adjuest_to + f"{scale}%",
            self._scaling_will_take_effect_after_restarting,
            self.window(),
        )
        w.yesButton.setText(self._restart_now)
        w.cancelButton.setText(self._restart_later)

        # 如果用户选择立即重启则重启应用程序
        if w.exec():
            utils.restart()

    def language_changed(self, _: str):
        """语言改变时的处理 - 更新界面翻译和重置UI"""
        self.window().translateUI()  # type:ignore  # 更新所有界面文本翻译
        self.window().resetUI()  # type:ignore      # 重置界面样式和字体

    def resetUI(self):
        """重置界面 - 更新字体设置"""
        setFont(self.rom_group.titleLabel, 16)  # 重置ROM设置组标题字体
        setFont(self.ui_group.titleLabel, 16)  # 重置界面设置组标题字体
        self.ffont.resetUI()  # 重置字体设置卡片

    def translateUI(self):
        """更新所有界面文本的翻译"""
        # 更新设置组标题
        self.rom_group.titleLabel.setText(self.tr("Rom Settings"))
        self.ui_group.titleLabel.setText(self.tr("Interface Settings"))

        # 更新各个设置卡片的翻译
        self.language.titleLabel.setText(self.tr("Interface Language"))
        self.language.contentLabel.setText(self.tr("Change the language of the interface"))
        self.theme.card.titleLabel.setText(self.tr("Theme Mode"))
        self.theme.card.contentLabel.setText(self.tr("Change the theme mode of the interface"))

        # 更新主题模式选项按钮文本
        self.theme.buttonGroup.buttons()[0].setText(self.tr("Light"))
        self.theme.buttonGroup.buttons()[1].setText(self.tr("Dark"))
        self.theme.buttonGroup.buttons()[2].setText(self.tr("Follow System"))
        self.theme.choiceLabel.setText(self.theme.buttonGroup.checkedButton().text())

        # 更新DPI设置卡片
        self.dpi.titleLabel.setText(self.tr("Interface Scaling"))
        self.dpi.contentLabel.setText(self.tr("Change the scaling ratio of the interface"))

        # 更新DPI对话框文本
        self._interface_scaling_adjuest_to = self.tr("Interface scaling adjusted to")
        self._scaling_will_take_effect_after_restarting = self.tr("Scaling will take effect after restarting the interface")
        self._restart_now = self.tr("Restart Now")
        self._restart_later = self.tr("Restart Later")

        # 更新子组件翻译
        self.color.translateUI()
        self.rom_card.translateUI()
        self.ffont.translateUI()
