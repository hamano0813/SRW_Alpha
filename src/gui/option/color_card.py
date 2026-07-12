"""
颜色设置卡片模块

提供主题颜色选择功能，支持默认颜色和自定义颜色两种模式。
扩展了原生 CustomColorSettingCard 以支持国际化翻译。

Classes:
    ColorCard: 支持国际化的主题颜色设置卡片
"""

from qfluentwidgets import ColorDialog, CustomColorSettingCard, qconfig


class ColorCard(CustomColorSettingCard):
    """主题颜色设置卡片 - 支持国际化的颜色选择器"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._choose_color = self.tr("Choose Color")
        self._ok = self.tr("OK")
        self._cancel = self.tr("Cancel")
        self._edit_color = self.tr("Edit Color")
        self._red = self.tr("Red")
        self._blue = self.tr("Blue")
        self._green = self.tr("Green")
        self._opacity = self.tr("Opacity")

    def _CustomColorSettingCard__showColorDialog(self):
        """
        显示颜色选择对话框

        重写父类的私有方法以支持国际化翻译。
        使用名称修饰（__name mangling）访问父类的私有方法。
        """
        w = ColorDialog(qconfig.get(self.configItem), self._choose_color, self.window(), self.enableAlpha)

        w.yesButton.setText(self._ok)
        w.cancelButton.setText(self._cancel)
        w.editLabel.setText(self._edit_color)
        w.redLabel.setText(self._red)
        w.blueLabel.setText(self._blue)
        w.greenLabel.setText(self._green)
        w.opacityLabel.setText(self._opacity)

        w.colorChanged.connect(self._CustomColorSettingCard__onCustomColorChanged)  # type: ignore
        w.exec()

    def translateUI(self):
        """更新所有界面文本的翻译"""
        self._choose_color = self.tr("Choose Color")
        self._ok = self.tr("OK")
        self._cancel = self.tr("Cancel")
        self._edit_color = self.tr("Edit Color")
        self._red = self.tr("Red")
        self._blue = self.tr("Blue")
        self._green = self.tr("Green")
        self._opacity = self.tr("Opacity")

        self.defaultRadioButton.setText(self.tr("Default color"))
        self.customRadioButton.setText(self.tr("Custom color"))
        self.customLabel.setText(self.tr("Custom color"))
        self.chooseColorButton.setText(self.tr("Choose Color"))
        self.choiceLabel.setText(self.buttonGroup.checkedButton().text())

        self.card.titleLabel.setText(self.tr("Theme Color"))
        self.card.contentLabel.setText(self.tr("Change the theme color of the interface"))
