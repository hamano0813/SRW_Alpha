"""
语言设置卡片模块

提供语言选择功能，支持多语言下拉菜单预览。
为每种语言选项使用对应的字体进行显示。
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
        """显示下拉菜单 - 为每个语言选项应用对应的字体"""
        super()._showComboMenu()
        if self.dropMenu:
            # 创建各语言字体对象
            en_font, zh_font, tw_font, jp_font = getFont(), getFont(), getFont(), getFont()
            # 设置各语言的字体系列
            en_font.setFamily(config.option.get(config.option.en_font))  # 英文字体
            zh_font.setFamily(config.option.get(config.option.cn_font))  # 简体中文字体
            tw_font.setFamily(config.option.get(config.option.tw_font))  # 繁体中文字体
            jp_font.setFamily(config.option.get(config.option.jp_font))  # 日文字体

            # 为下拉菜单项应用对应字体（按固定顺序：英文、简中、繁中、日文）
            self.dropMenu.view.item(0).setFont(en_font)
            self.dropMenu.view.item(1).setFont(zh_font)
            self.dropMenu.view.item(2).setFont(tw_font)
            self.dropMenu.view.item(3).setFont(jp_font)


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

        # 移除原有的组合框组件
        self.comboBox.currentIndexChanged.disconnect(self._onCurrentIndexChanged)
        self.hBoxLayout.removeWidget(self.comboBox)
        self.hBoxLayout.removeItem(self.hBoxLayout.itemAt(self.hBoxLayout.count() - 1))
        self.comboBox.close()
        self.comboBox.deleteLater()

        # 创建并添加自定义语言组合框
        self.comboBox = LanguageCombo(self)
        self.hBoxLayout.addWidget(self.comboBox, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.addSpacing(16)

        # 初始化语言选项
        if not texts:
            texts = []
        # 创建语言选项到显示文本的映射
        self.optionToText = {o: t for o, t in zip(config.option.language.options, texts)}
        # 添加语言选项到组合框
        for text, option in zip(texts, config.option.language.options):
            self.comboBox.addItem(text, userData=option)
        # 设置当前选中的语言
        self.comboBox.setCurrentText(self.optionToText[config.qconfig.get(config.option.language)])
        # 重新连接选择改变信号
        self.comboBox.currentIndexChanged.connect(self._onCurrentIndexChanged)
