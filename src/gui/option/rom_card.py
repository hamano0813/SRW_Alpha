"""
ROM 文件配置卡片模块

提供 ROM 文件路径选择和配置的用户界面组件。
包含源/目标 ROM 路径选择功能和缓存清理设置卡片。

Classes:
    CardType: 卡片类型枚举（SOURCE / TARGET）
    FileSettingCard: 文件路径设置卡片
    CleanSettingCard: 缓存清理设置卡片
    RomCard: ROM 文件组设置卡片
"""

import os
from enum import Enum
from typing import Union

from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileDialog
from qfluentwidgets import (
    ConfigItem,
    ExpandGroupSettingCard,
    FluentIconBase,
    MessageBox,
    PushSettingCard,
    SwitchSettingCard,
    qconfig,
    setCustomStyleSheet,
)

import config


class CardType(Enum):
    SOURCE = 0
    TARGET = 1


class CustomCard:
    def translateUI(self):
        pass


class FileSettingCard(PushSettingCard, CustomCard):
    """文件路径设置卡片"""

    pathChanged = Signal()

    def __init__(self, path: ConfigItem, title: str, ctype: CardType, parent=None):
        super().__init__("", "", "", "", parent)
        self._select_file = self.tr("Select File")

        self._path = path
        self._title = title
        self._ctype = ctype

        self._non_ascii_title = self.tr("Non-ASCII Path")
        self._non_ascii_msg = self.tr("ROM path and filename cannot contain non-ASCII characters.")
        self._ok = self.tr("OK")

        self.titleLabel.setText(title)
        self.contentLabel.setText(path.value)
        self.contentLabel.setHidden(False)
        setCustomStyleSheet(self, "QFrame {border: none;}", "QFrame {border: none;}")

        self.button.clicked.connect(self.select_file)

        self.translateUI()

    def select_file(self):
        """打开文件选择对话框，选择 ROM 文件路径后保存并检查 ASCII 合规"""
        if self._ctype is CardType.SOURCE:
            file_path, _ = QFileDialog.getOpenFileName(self, self._select_file, "", "ROM Files (*.bin *.cue)")
        else:
            file_path, _ = QFileDialog.getSaveFileName(self, self._select_file, config.option.get(self._path), "ROM Files (*.bin *.cue)")
        if file_path:
            if not file_path.isascii():
                w = MessageBox(
                    self._non_ascii_title,
                    self._non_ascii_msg,
                    self.window(),
                )
                w.yesButton.setText(self._ok)
                w.cancelButton.hide()
                w.exec()
                return

            config.option.set(self._path, file_path)
            self.contentLabel.setText(file_path)
            self.pathChanged.emit()

    def translateUI(self):
        """更新界面文本翻译"""
        self.button.setText(self.tr("Browse"))
        self._select_file = self.tr("Select File")
        self.titleLabel.setText(self._title)

        self._non_ascii_title = self.tr("Non-ASCII Path")
        self._non_ascii_msg = self.tr("ROM path and filename cannot contain non-ASCII characters.")
        self._ok = self.tr("OK")

    def paintEvent(self, e):
        pass


class CleanSettingCard(SwitchSettingCard, CustomCard):
    def __init__(self, configItem: ConfigItem, parent=None):
        super().__init__("", "", "", configItem, parent)
        self.switchButton.setOnText("")
        self.switchButton.setOffText("")
        self.titleLabel.setText(self.tr("Auto clear cache"))
        self.contentLabel.setText(self.tr("Clear cache after ROM is rebuilt"))
        self.contentLabel.setHidden(False)

    def translateUI(self):
        self.titleLabel.setText(self.tr("Auto clear cache"))
        self.contentLabel.setText(self.tr("Clear cache after ROM is rebuilt"))

    def setValue(self, isChecked: bool):
        if self.configItem:
            qconfig.set(self.configItem, isChecked)
        self.switchButton.setChecked(isChecked)

    def paintEvent(self, e):
        pass


class RomCard(ExpandGroupSettingCard):
    """ROM 文件组设置卡片 - 可展开的设置组"""

    def __init__(self, icon: Union[str, QIcon, FluentIconBase], parent=None):
        super().__init__(icon, self.tr("ROM Settings"), self.tr("Configure the ROM settings"), parent)  # type: ignore

        self._source_card = FileSettingCard(config.option.source_rom, self.tr("Source ROM"), CardType.SOURCE, self)
        self._target_card = FileSettingCard(config.option.target_rom, self.tr("Target ROM"), CardType.TARGET, self)
        self._clean_card = CleanSettingCard(config.option.auto_clean, self)

        self.addGroupWidget(self._source_card)
        self.addGroupWidget(self._target_card)
        self.addGroupWidget(self._clean_card)

        self._source_card.pathChanged.connect(self._on_source_rom_changed)

    def _on_source_rom_changed(self):
        """SOURCE ROM 路径更新后，自动设置 TARGET ROM 路径为 SOURCE 文件名 + _TEMP"""
        source_rom = config.option.source_rom.value
        if not source_rom:
            return
        base, ext = os.path.splitext(source_rom)
        target_rom = base + "_TEMP" + ext
        config.option.set(config.option.target_rom, target_rom)
        self._target_card.contentLabel.setText(target_rom)

    def translateUI(self):
        """更新组卡片和所有子卡片的界面翻译"""
        self.card.titleLabel.setText(self.tr("ROM Settings"))
        self.card.contentLabel.setText(self.tr("Configure the ROM settings"))
        self._source_card._title = self.tr("Source ROM")
        self._target_card._title = self.tr("Target ROM")
        for widget in self.widgets:
            if isinstance(widget, CustomCard):
                widget.translateUI()
