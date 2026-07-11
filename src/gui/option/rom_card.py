"""
ROM文件配置卡片模块

提供ROM文件路径选择和配置的用户界面组件。
包含ROM文件读写的路径选择功能和缓存清理设置卡片。
"""

from enum import Enum
from typing import Union

from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileDialog
from qfluentwidgets import (
    ConfigItem,
    ExpandGroupSettingCard,
    FluentIconBase,
    PushSettingCard,
    SwitchSettingCard,
    qconfig,
    setCustomStyleSheet,
)

import config


class CardType(Enum):
    LOAD = 0
    SAVE = 1


class CustomCard:
    def translateUI(self):
        pass


class FileSettingCard(PushSettingCard, CustomCard):
    """文件路径设置卡片"""

    pathChanged = Signal()  # ROM文件路径改变时发出的信号

    def __init__(self, path: ConfigItem, title: str, ctype: CardType, parent=None):
        super().__init__("", "", "", "", parent)
        self._select_file = self.tr("Select File")

        self._path = path
        self._title = title
        self._ctype = ctype
        self.titleLabel.setText(title)
        self.contentLabel.setText(path.value)  # 显示当前文件路径
        self.contentLabel.setHidden(False)  # 确保路径标签可见
        # 移除边框样式，与主题保持一致
        setCustomStyleSheet(self, "QFrame {border: none;}", "QFrame {border: none;}")

        self.button.clicked.connect(self.select_file)

        self.translateUI()

    def select_file(self):
        if self._ctype is CardType.LOAD:
            """打开文件选择对话框选择读取文件路径"""
            file_path, _ = QFileDialog.getOpenFileName(self, self._select_file, "", "ROM Files (*.bin *.cue)")
        else:
            """打开文件选择对话框选择保存文件路径"""
            file_path, _ = QFileDialog.getSaveFileName(self, self._select_file, "", "ROM Files (*.bin *.cue)")
        if file_path:
            # 保存选择的文件路径到配置
            config.option.set(self._path, file_path)
            self.contentLabel.setText(file_path)  # 更新显示的路径
            self.pathChanged.emit()  # 发出文件改变信号

    def translateUI(self):
        """更新界面文本翻译"""
        self.button.setText(self.tr("Browse"))
        self._select_file = self.tr("Select File")
        self.titleLabel.setText(self._title)

    def paintEvent(self, e):
        """重写绘制事件 - 禁用默认绘制"""
        pass


class CleanSettingCard(SwitchSettingCard, CustomCard):
    def __init__(self, configItem: ConfigItem, parent=None):
        super().__init__("", "", "", configItem, parent)
        self.switchButton.setOnText("")
        self.switchButton.setOffText("")
        self.contentLabel.setHidden(False)  # 确保提示标签可见

    def translateUI(self):
        self.titleLabel.setText(self.tr("Auto clear cache"))
        self.contentLabel.setText(self.tr("Clear cache after ROM is saved"))

    def setValue(self, isChecked: bool):
        if self.configItem:
            qconfig.set(self.configItem, isChecked)
        self.switchButton.setChecked(isChecked)

    def paintEvent(self, e):
        """重写绘制事件 - 禁用默认绘制"""
        pass

class RomCard(ExpandGroupSettingCard):
    """ROM文件组设置卡片 - 可展开的设置组"""

    def __init__(self, icon: Union[str, QIcon, FluentIconBase], parent=None):
        super().__init__(icon, self.tr("ROM Settings"), self.tr("Configure the ROM settings"), parent)  # type: ignore

        self._load_card = FileSettingCard(config.option.load_path, self.tr("Load ROM"), CardType.LOAD, self)
        self._save_card = FileSettingCard(config.option.save_path, self.tr("Save ROM"), CardType.SAVE, self)
        self._clean_card = CleanSettingCard(config.option.auto_clean, self)

        self.addGroupWidget(self._load_card)
        self.addGroupWidget(self._save_card)
        self.addGroupWidget(self._clean_card)

    def translateUI(self):
        """更新组卡片和所有子卡片的界面翻译"""
        self.card.titleLabel.setText(self.tr("ROM Settings"))
        self.card.contentLabel.setText(self.tr("Configure the ROM settings"))
        self._load_card._title = self.tr("Load ROM")
        self._save_card._title = self.tr("Save ROM")
        # 遍历所有子组件更新翻译
        for widget in self.widgets:
            if isinstance(widget, CustomCard):
                widget.translateUI()
