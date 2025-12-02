from typing import cast

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QFontDatabase
from qfluentwidgets import (
    ComboBox,
    ConfigItem,
    ExpandGroupSettingCard,
    SettingCard,
    fontStyleSheet,
    getFont,
)

import config
from core import utils
from gui.custom import CustomIcon


class FamilyCombo(ComboBox):
    familyChanged = Signal(str, str)
    WS = {
        QFontDatabase.WritingSystem.SimplifiedChinese: 0x804,
        QFontDatabase.WritingSystem.TraditionalChinese: 0x404,
        QFontDatabase.WritingSystem.Japanese: 0x411,
    }

    def __init__(self, font_mapping: dict[str, str], writing_system: QFontDatabase.WritingSystem, parent=None):
        super().__init__(parent)
        self.db = QFontDatabase()
        self.writing_system = writing_system
        self.font_mapping = font_mapping

        self.init_families()
        self.setFixedWidth(400)

        self.currentIndexChanged.connect(self.family_changed)
        self.resetUI()

    def family_changed(self, index):
        name = self.itemText(index)
        family = self.currentData()
        self.familyChanged.emit(name, family)

    def get_family(self, userdata: str) -> str:
        for name, family in self.fonts.items():
            if family == userdata:
                return name
        return ""

    def init_families(self):
        families: list[str] = [f for f in self.db.families(self.writing_system) if self.db.isSmoothlyScalable(f)]
        self.fonts = {}
        for family in families:
            if not family.isascii():
                self.fonts[family] = family
            elif family in self.font_mapping:
                name = utils.get_font_info(self.font_mapping[family], self.WS.get(self.writing_system, 0x409))
                if name not in self.fonts:
                    self.fonts[name] = family
            else:
                if family not in self.fonts:
                    self.fonts[family] = family
        self.fonts.pop("", None)
        for name, family in sorted(self.fonts.items()):
            self.addItem(name, userData=family)

    def resetUI(self):
        family = self.currentData()
        family = cast(str, family)
        font = getFont()
        font.setFamilies([family])
        self.setFont(font)
        self.setStyleSheet(fontStyleSheet(font))

    def _showComboMenu(self):
        super()._showComboMenu()
        if self.dropMenu:
            for i in range(self.dropMenu.view.count()):
                font = getFont()
                font.setFamilies([self.dropMenu.actions()[i].text(), "Segoe UI"])
                self.dropMenu.view.item(i).setFont(font)


class FontFamilyCard(SettingCard):
    def __init__(
        self,
        font_config: ConfigItem,
        title: str,
        font_mapping: dict[str, str],
        writing_system: QFontDatabase.WritingSystem,
        parent=None,
    ):
        super().__init__("", title, parent=parent)
        self.font_config = font_config
        self.familyCombo = FamilyCombo(font_mapping, writing_system, self)
        self.hBoxLayout.addWidget(self.familyCombo, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(16)
        self.familyChanged = self.familyCombo.familyChanged

        self.familyCombo.setCurrentText(self.familyCombo.get_family(config.qconfig.get(font_config)))
        self.familyChanged.connect(self.current_changed)
        self.resetUI()

    def current_changed(self, _: str, family: str):
        config.qconfig.set(self.font_config, family)

    def resetUI(self):
        family = [config.qconfig.get(self.font_config)] + config.option.get(config.option.fontFamilies)
        font = getFont(16, weight=QFont.Weight.Bold)
        font.setFamilies(family)
        self.titleLabel.setStyleSheet(fontStyleSheet(font))
        self.familyCombo.resetUI()


class FontLoadThread(QThread):
    loadFinished = Signal(dict)

    def run(self):
        mapping = utils.get_font_mapping()
        self.loadFinished.emit(mapping)


class FontCard(ExpandGroupSettingCard):
    familyChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(CustomIcon.FONT.icon(), self.tr("Font Settings"), self.tr("Configure the font settings"), parent)

        self.font_mapping = {}
        self.fm_thread = FontLoadThread()
        self.fm_thread.loadFinished.connect(self.init_fonts)
        self.fm_thread.start()

    def init_fonts(self, mapping: dict[str, str]):
        self.font_mapping = mapping
        self.fm_thread.quit()
        self.fm_thread.wait()
        self.addFont(config.option.en_font)
        self.addFont(config.option.cn_font)
        self.addFont(config.option.tw_font)
        self.addFont(config.option.jp_font)

    def addFont(self, font_config: ConfigItem):
        mapping = {
            "ENFont": ["Super Robot Wars α", QFontDatabase.WritingSystem.Any],
            "CNFont": ["超级机器人大战 α", QFontDatabase.WritingSystem.SimplifiedChinese],
            "TWFont": ["超級機器人大戰 α", QFontDatabase.WritingSystem.TraditionalChinese],
            "JPFont": ["スーパーロボット大戦 α", QFontDatabase.WritingSystem.Japanese],
        }
        title, writing_system = mapping.get(font_config.name, ["English", QFontDatabase.WritingSystem.Any])

        font_family_card = FontFamilyCard(font_config, title, self.font_mapping, writing_system, self)
        self.addGroupWidget(font_family_card)
        font_family_card.familyChanged.connect(self.family_changed)

    def family_changed(self, *_):
        self.familyChanged.emit()

    def resetUI(self):
        for card in self.widgets:
            card = cast(FontFamilyCard, card)
            card.resetUI()

    def translateUI(self):
        self.card.titleLabel.setText(self.tr("Font Settings"))
        self.card.contentLabel.setText(self.tr("Configure the font settings"))
