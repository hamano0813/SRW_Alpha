"""
语言设置卡片模块

提供语言选择功能，支持多语言下拉菜单预览。
每种语言选项在菜单中使用对应的字体显示。

Classes:
    LanguageCombo: 语言选择组合框 - 为每种语言使用对应字体显示
    LanguageCard: 语言设置卡片 - 使用自定义语言组合框替换默认组合框
"""

from typing import Union

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from qfluentwidgets import (
    ComboBox,
    ComboBoxSettingCard,
    FluentIconBase,
    OptionsConfigItem,
    getFont,
)

import config


class LanguageCombo(ComboBox):
    """语言选择组合框 - 为每种语言使用对应字体显示"""

    def _showComboMenu(self):
        """显示下拉菜单 - 为每个语言选项设置对应字体"""
        super()._showComboMenu()
        if self.dropMenu:
            en_font, zh_font, jp_font = getFont(), getFont(), getFont()
            en_font.setFamily(config.option.get(config.option.en_font))
            zh_font.setFamily(config.option.get(config.option.cn_font))
            jp_font.setFamily(config.option.get(config.option.jp_font))

            self.dropMenu.view.item(0).setFont(en_font)
            self.dropMenu.view.item(1).setFont(zh_font)
            self.dropMenu.view.item(2).setFont(jp_font)


class LanguageCard(ComboBoxSettingCard):
    """语言设置卡片 - 使用自定义语言组合框替换默认组合框"""

    def __init__(
        self,
        configItem: OptionsConfigItem,
        icon: Union[str, QIcon, FluentIconBase],
        title: str,
        content=None,
        texts: list | None = None,
        parent=None,
    ):
        super().__init__(configItem, icon, title, content, texts, parent)

        self.comboBox.currentIndexChanged.disconnect(self._onCurrentIndexChanged)
        self.hBoxLayout.removeWidget(self.comboBox)
        self.hBoxLayout.removeItem(self.hBoxLayout.itemAt(self.hBoxLayout.count() - 1))
        self.comboBox.close()
        self.comboBox.deleteLater()

        self.comboBox = LanguageCombo(self)
        self.hBoxLayout.addWidget(self.comboBox, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(16)

        if not texts:
            texts = []
        self.optionToText = {o: t for o, t in zip(config.option.language.options, texts)}
        for text, option in zip(texts, config.option.language.options):
            self.comboBox.addItem(text, userData=option)
        self.comboBox.setCurrentText(self.optionToText[config.qconfig.get(config.option.language)])
        self.comboBox.currentIndexChanged.connect(self._onCurrentIndexChanged)
