"""
ROM文件配置卡片模块

提供ROM文件路径选择和配置的用户界面组件。
包含单个ROM文件设置卡片和ROM文件组设置卡片。
"""

from typing import Union

from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QFileDialog
from qfluentwidgets import (
    ConfigItem,
    ExpandGroupSettingCard,
    FluentIconBase,
    PushSettingCard,
    setCustomStyleSheet,
)

import config
from gui.custom import CustomIcon


class RomSettingCard(PushSettingCard):
    """单个ROM文件设置卡片"""

    romChanged = Signal()  # ROM文件路径改变时发出的信号

    def __init__(self, rom: ConfigItem, parent=None):
        super().__init__("", "", "", "", parent)
        self._select_file = self.tr("Select File")

        self._rom = rom
        self.titleLabel.setText(rom.name)  # 显示ROM文件名称
        self.contentLabel.setText(rom.value)  # 显示当前文件路径
        self.contentLabel.setHidden(False)  # 确保路径标签可见
        # 移除边框样式，与主题保持一致
        setCustomStyleSheet(self, "QFrame {border: none;}", "QFrame {border: none;}")

        self.button.clicked.connect(self.select_rom)

        self.translateUI()

    def select_rom(self):
        """打开文件选择对话框选择ROM文件"""
        # 使用文件对话框选择ROM文件，过滤器为当前ROM类型
        rom_path, _ = QFileDialog.getOpenFileName(self, self._select_file, "", f"{self._rom.name}")
        if rom_path:
            # 保存选择的文件路径到配置
            config.option.set(self._rom, rom_path)
            self.contentLabel.setText(rom_path)  # 更新显示的路径
            self.romChanged.emit()  # 发出文件改变信号

    def translateUI(self):
        """更新界面文本翻译"""
        self.button.setText(self.tr("Browse"))
        self._select_file = self.tr("Select File")

    def paintEvent(self, e):
        """重写绘制事件 - 禁用默认绘制"""
        pass


class RomCard(ExpandGroupSettingCard):
    """ROM文件组设置卡片 - 可展开的设置组"""

    def __init__(self, icon: Union[str, QIcon, FluentIconBase], parent=None):
        super().__init__(icon, self.tr("Rom Files"), self.tr("Configure the ROM file paths"), parent)  # type: ignore

        # 添加所有ROM文件配置项
        self.addRom(config.option.robot_raf)  # 机体数据
        self.addRom(config.option.pilot_bin)  # 驾驶员数据
        self.addRom(config.option.snmsg_bin)  # 剧情文本
        self.addRom(config.option.sndata_bin)  # 剧情数据
        self.addRom(config.option.enlist_bin)  # 敌方单位列表
        self.addRom(config.option.aiunp_bin)  # AI数据
        self.addRom(config.option.script_bin)  # 脚本数据
        self.addRom(config.option.prm_grp_bin)  # 参数组

    def addRom(self, rom_config: ConfigItem):
        """添加单个ROM文件设置卡片到组中"""
        rom_setting_card = RomSettingCard(rom_config, self)
        self.addGroupWidget(rom_setting_card)

    def translateUI(self):
        """更新组卡片和所有子卡片的界面翻译"""
        self.card.titleLabel.setText(self.tr("Rom Files"))
        self.card.contentLabel.setText(self.tr("Configure the ROM file paths"))
        # 遍历所有子组件更新翻译
        for widget in self.widgets:
            if isinstance(widget, RomSettingCard):
                widget.translateUI()
