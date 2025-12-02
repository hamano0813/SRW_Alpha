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
    def _showComboMenu(self):
        super()._showComboMenu()
        if self.dropMenu:
            en_font, zh_font, tw_font, jp_font = getFont(), getFont(), getFont(), getFont()
            en_font.setFamily(config.option.get(config.option.en_font))
            zh_font.setFamily(config.option.get(config.option.cn_font))
            tw_font.setFamily(config.option.get(config.option.tw_font))
            jp_font.setFamily(config.option.get(config.option.jp_font))
            self.dropMenu.view.item(0).setFont(en_font)
            self.dropMenu.view.item(1).setFont(zh_font)
            self.dropMenu.view.item(2).setFont(tw_font)
            self.dropMenu.view.item(3).setFont(jp_font)


class LanguageCard(ComboBoxSettingCard):
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
