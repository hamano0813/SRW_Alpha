"""
字体设置卡片模块

提供字体选择和配置功能，支持多语言字体设置。
包含字体组合框、单个字体设置卡片和字体设置组等组件。
"""

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
    """字体系列选择组合框 - 支持多语言字体显示和预览"""

    familyChanged = Signal(str, str)  # 字体改变信号：(显示名称, 字体系列)

    # 书写系统对应的语言ID映射
    WS = {
        QFontDatabase.WritingSystem.SimplifiedChinese: 0x804,
        QFontDatabase.WritingSystem.TraditionalChinese: 0x404,
        QFontDatabase.WritingSystem.Japanese: 0x411,
    }

    def __init__(self, font_mapping: dict[str, str], writing_system: QFontDatabase.WritingSystem, parent=None):
        super().__init__(parent)
        self.db = QFontDatabase()
        self.writing_system = writing_system  # 当前书写系统
        self.font_mapping = font_mapping  # 字体文件路径映射

        self.init_families()
        self.setFixedWidth(400)

        self.currentIndexChanged.connect(self.family_changed)
        self.resetUI()

    def family_changed(self, index):
        """字体选择改变时的处理"""
        name = self.itemText(index)  # 获取显示名称
        family = self.currentData()  # 获取实际字体系列名
        self.familyChanged.emit(name, family)

    def get_family(self, userdata: str) -> str:
        """根据字体系列名获取显示名称"""
        for name, family in self.fonts.items():
            if family == userdata:
                return name
        return ""

    def init_families(self):
        """初始化字体列表 - 获取支持当前书写系统的可缩放字体"""
        # 获取支持当前书写系统且可平滑缩放的字体
        families: list[str] = [f for f in self.db.families(self.writing_system) if self.db.isSmoothlyScalable(f)]
        self.fonts = {}

        for family in families:
            if not family.isascii():
                # 非ASCII字体名称直接使用
                self.fonts[family] = family
            elif family in self.font_mapping:
                # 从字体文件中提取本地化名称
                name = utils.get_font_info(self.font_mapping[family], self.WS.get(self.writing_system, 0x409))
                if name not in self.fonts:
                    self.fonts[name] = family
            else:
                # 使用字体系列名作为显示名称
                if family not in self.fonts:
                    self.fonts[family] = family

        # 移除空名称的字体
        self.fonts.pop("", None)
        # 按字母顺序添加到下拉列表
        for name, family in sorted(self.fonts.items()):
            self.addItem(name, userData=family)

    def resetUI(self):
        """重置界面 - 使用当前选中的字体更新组合框显示"""
        family = self.currentData()
        family = cast(str, family)
        font = getFont()
        font.setFamilies([family])  # 设置字体系列
        self.setFont(font)
        self.setStyleSheet(fontStyleSheet(font))

    def _showComboMenu(self):
        """显示下拉菜单 - 为每个菜单项应用对应的字体预览"""
        super()._showComboMenu()
        if self.dropMenu:
            # 为下拉菜单中的每个项目设置对应的字体预览
            for i in range(self.dropMenu.view.count()):
                font = getFont()
                # 设置字体系列，Segoe UI作为回退字体
                font.setFamilies([self.dropMenu.actions()[i].text(), "Segoe UI"])
                self.dropMenu.view.item(i).setFont(font)


class FontFamilyCard(SettingCard):
    """单个字体系列设置卡片"""

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
        # 创建字体选择组合框
        self.familyCombo = FamilyCombo(font_mapping, writing_system, self)
        self.hBoxLayout.addWidget(self.familyCombo, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(16)
        self.familyChanged = self.familyCombo.familyChanged

        # 设置当前字体为配置中的字体
        self.familyCombo.setCurrentText(self.familyCombo.get_family(config.qconfig.get(font_config)))
        self.familyChanged.connect(self.current_changed)
        self.resetUI()

    def current_changed(self, _: str, family: str):
        """字体选择改变时保存到配置"""
        config.qconfig.set(self.font_config, family)

    def resetUI(self):
        """重置界面 - 使用选定字体更新标题显示"""
        # 构建字体优先级列表：当前字体 + 全局字体回退列表
        family = [config.qconfig.get(self.font_config)] + config.option.get(config.option.fontFamilies)
        font = getFont(16, weight=QFont.Weight.Bold)
        font.setFamilies(family)
        self.titleLabel.setStyleSheet(fontStyleSheet(font))  # 标题使用选定字体显示
        self.familyCombo.resetUI()


class FontLoadThread(QThread):
    """字体映射加载线程 - 在后台加载字体文件映射信息"""

    loadFinished = Signal(dict)  # 加载完成信号，传递字体映射字典

    def run(self):
        """在后台线程中获取字体映射"""
        mapping = utils.get_font_mapping()  # 扫描系统字体文件
        self.loadFinished.emit(mapping)


class FontCard(ExpandGroupSettingCard):
    """字体设置组卡片 - 管理所有语言的字体配置"""

    familyChanged = Signal()  # 任何字体改变时发出的信号

    def __init__(self, parent=None):
        super().__init__(CustomIcon.FONT.icon(), self.tr("Font Settings"), self.tr("Configure the font settings"), parent)

        self.font_mapping = {}
        # 启动后台线程加载字体映射
        self.fm_thread = FontLoadThread()
        self.fm_thread.loadFinished.connect(self.init_fonts)
        self.fm_thread.start()

    def init_fonts(self, mapping: dict[str, str]):
        """初始化字体设置 - 字体映射加载完成后创建各语言字体设置卡片"""
        self.font_mapping = mapping
        # 清理后台线程
        self.fm_thread.quit()
        self.fm_thread.wait()

        # 添加各语言字体配置
        self.addFont(config.option.en_font)  # 英文字体
        self.addFont(config.option.cn_font)  # 简体中文字体
        self.addFont(config.option.tw_font)  # 繁体中文字体
        self.addFont(config.option.jp_font)  # 日文字体

    def addFont(self, font_config: ConfigItem):
        """添加单个字体设置卡片"""
        # 字体配置名称到显示标题和书写系统的映射
        mapping = {
            "ENFont": ["Super Robot Wars α", QFontDatabase.WritingSystem.Any],
            "CNFont": ["超级机器人大战 α", QFontDatabase.WritingSystem.SimplifiedChinese],
            "TWFont": ["超級機器人大戰 α", QFontDatabase.WritingSystem.TraditionalChinese],
            "JPFont": ["スーパーロボット大戦 α", QFontDatabase.WritingSystem.Japanese],
        }
        title, writing_system = mapping.get(font_config.name, ["English", QFontDatabase.WritingSystem.Any])

        # 创建字体设置卡片并添加到组中
        font_family_card = FontFamilyCard(font_config, title, self.font_mapping, writing_system, self)
        self.addGroupWidget(font_family_card)
        font_family_card.familyChanged.connect(self.family_changed)

    def family_changed(self, *_):
        """任何字体改变时发出信号通知外部组件"""
        self.familyChanged.emit()

    def resetUI(self):
        """重置所有字体设置卡片的界面"""
        for card in self.widgets:
            card = cast(FontFamilyCard, card)
            card.resetUI()

    def translateUI(self):
        """更新字体设置组的界面翻译"""
        self.card.titleLabel.setText(self.tr("Font Settings"))
        self.card.contentLabel.setText(self.tr("Configure the font settings"))
