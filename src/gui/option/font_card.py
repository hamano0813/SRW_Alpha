"""
字体设置卡片模块

提供字体选择和配置功能，支持多语言字体设置。
包含字体组合框、单个字体设置卡片和字体设置组等组件。

Classes:
    FamilyCombo: 字体系列选择组合框
    FontFamilyCard: 单个字体系列设置卡片
    FontLoadThread: 字体映射加载线程
    FontCard: 字体设置组卡片
"""

from typing import Union, cast

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QFontDatabase, QIcon
from qfluentwidgets import (
    ComboBox,
    ConfigItem,
    ExpandGroupSettingCard,
    FluentIconBase,
    SettingCard,
    fontStyleSheet,
    getFont,
)

import config
import utils


class FamilyCombo(ComboBox):
    """字体系列选择组合框 - 支持多语言字体显示和预览"""

    familyChanged = Signal(str, str)

    WS = {
        QFontDatabase.WritingSystem.SimplifiedChinese: 0x804,
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
        """字体选择改变时发出信号"""
        name = self.itemText(index)
        family = self.currentData()
        self.familyChanged.emit(name, family)

    def get_family(self, userdata: str) -> str:
        """根据字体系列名获取显示名称"""
        for name, family in self.fonts.items():
            if family == userdata:
                return name
        return ""

    def init_families(self):
        """初始化字体列表 - 获取支持当前书写系统的可缩放字体"""
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
        """使用当前选中字体更新组合框显示"""
        family = self.currentData()
        family = cast(str, family)
        font = getFont()
        font.setFamilies([family])
        self.setFont(font)
        self.setStyleSheet(fontStyleSheet(font))

    def _showComboMenu(self):
        """显示下拉菜单 - 每个菜单项使用对应字体预览"""
        super()._showComboMenu()
        if self.dropMenu:
            for i in range(self.dropMenu.view.count()):
                font = getFont()
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
        self.familyCombo = FamilyCombo(font_mapping, writing_system, self)
        self.hBoxLayout.addWidget(self.familyCombo, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(16)
        self.familyChanged = self.familyCombo.familyChanged

        self.familyCombo.setCurrentText(self.familyCombo.get_family(config.qconfig.get(font_config)))
        self.familyChanged.connect(self.current_changed)
        self.resetUI()

    def current_changed(self, _: str, family: str):
        """字体选择改变时保存到配置"""
        config.qconfig.set(self.font_config, family)

    def resetUI(self):
        """更新标题为当前选定字体样式"""
        family = [config.qconfig.get(self.font_config)] + config.option.get(config.option.fontFamilies)
        font = getFont(16, weight=QFont.Weight.Bold)
        font.setFamilies(family)
        self.titleLabel.setStyleSheet(fontStyleSheet(font))
        self.familyCombo.resetUI()

    def paintEvent(self, e):
        pass


class FontLoadThread(QThread):
    """字体映射加载线程 - 后台加载字体文件映射信息"""

    loadFinished = Signal(dict)

    def run(self):
        mapping = utils.get_font_mapping()
        self.loadFinished.emit(mapping)


class FontCard(ExpandGroupSettingCard):
    """字体设置组卡片 - 管理所有语言的字体配置"""

    familyChanged = Signal()

    def __init__(self, icon: Union[str, QIcon, FluentIconBase], parent=None):
        super().__init__(icon, self.tr("Font Settings"), self.tr("Configure the font settings"), parent)  # type: ignore

        self.font_mapping = {}
        self.fm_thread = FontLoadThread()
        self.fm_thread.loadFinished.connect(self.init_fonts)
        self.fm_thread.start()

    def init_fonts(self, mapping: dict[str, str]):
        """字体映射加载完成后创建各语言字体设置卡片"""
        self.font_mapping = mapping
        self.fm_thread.quit()
        self.fm_thread.wait()

        self.addFont(config.option.en_font)
        self.addFont(config.option.cn_font)
        self.addFont(config.option.jp_font)

    def addFont(self, font_config: ConfigItem):
        """添加单个字体设置卡片"""
        mapping = {
            "ENFont": ["Super Robot Wars α", QFontDatabase.WritingSystem.Any],
            "CNFont": ["超级机器人大战 α", QFontDatabase.WritingSystem.SimplifiedChinese],
            "JPFont": ["スーパーロボット大戦 α", QFontDatabase.WritingSystem.Japanese],
        }
        title, writing_system = mapping.get(font_config.name, ["English", QFontDatabase.WritingSystem.Any])

        font_family_card = FontFamilyCard(font_config, title, self.font_mapping, writing_system, self)
        self.addGroupWidget(font_family_card)
        font_family_card.familyChanged.connect(self.family_changed)

    def family_changed(self, *_):
        """任何字体改变时发出信号通知外部组件"""
        self.familyChanged.emit()

    def resetUI(self):
        """重置所有字体设置卡片的显示"""
        for card in self.widgets:
            card = cast(FontFamilyCard, card)
            card.resetUI()

    def translateUI(self):
        """更新字体设置组的界面翻译"""
        self.card.titleLabel.setText(self.tr("Font Settings"))
        self.card.contentLabel.setText(self.tr("Configure the font settings"))
