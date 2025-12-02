from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog
from qfluentwidgets import (
    ConfigItem,
    ExpandGroupSettingCard,
    PushSettingCard,
    setCustomStyleSheet,
)

import config
from gui.custom import CustomIcon


class RomSettingCard(PushSettingCard):
    romChanged = Signal()

    def __init__(self, rom: ConfigItem, parent=None):
        super().__init__("", "", "", "", parent)
        self._select_file = self.tr("Select File")

        self._rom = rom
        self.titleLabel.setText(rom.name)
        self.contentLabel.setText(rom.value)
        self.contentLabel.setHidden(False)
        setCustomStyleSheet(self, "QFrame {border: none;}", "QFrame {border: none;}")

        self.button.clicked.connect(self.select_rom)

        self.translateUI()

    def select_rom(self):
        rom_path, _ = QFileDialog.getOpenFileName(self, self._select_file, "", f"{self._rom.name}")
        if rom_path:
            config.option.set(self._rom, rom_path)
            self.contentLabel.setText(rom_path)
            self.romChanged.emit()

    def translateUI(self):
        self.button.setText(self.tr("Browse"))
        self._select_file = self.tr("Select File")

    def paintEvent(self, e):
        pass


class RomCard(ExpandGroupSettingCard):
    def __init__(self, parent=None):
        super().__init__(CustomIcon.ROM.icon(), self.tr("Rom Files"), self.tr("Configure the ROM file paths"), parent)

        self.addRom(config.option.robot_raf)
        self.addRom(config.option.pilot_bin)
        self.addRom(config.option.snmsg_bin)
        self.addRom(config.option.sndata_bin)
        self.addRom(config.option.enlist_bin)
        self.addRom(config.option.aiunp_bin)
        self.addRom(config.option.script_bin)
        self.addRom(config.option.prm_grp_bin)

    def addRom(self, rom_config: ConfigItem):
        rom_setting_card = RomSettingCard(rom_config, self)
        self.addGroupWidget(rom_setting_card)

    def translateUI(self):
        self.card.titleLabel.setText(self.tr("Rom Files"))
        self.card.contentLabel.setText(self.tr("Configure the ROM file paths"))
        for widget in self.widgets:
            if isinstance(widget, RomSettingCard):
                widget.translateUI()
