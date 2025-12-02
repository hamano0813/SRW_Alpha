from qfluentwidgets import ColorDialog, CustomColorSettingCard, qconfig


class ColorCard(CustomColorSettingCard):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._choose_color = self.tr("Choose color")
        self._ok = self.tr("OK")
        self._cancel = self.tr("Cancel")
        self._edit_color = self.tr("Edit Color")
        self._red = self.tr("Red")
        self._blue = self.tr("Blue")
        self._green = self.tr("Green")
        self._opacity = self.tr("Opacity")

    def _CustomColorSettingCard__showColorDialog(self):
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
        self._choose_color = self.tr("Choose color")
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
        self.chooseColorButton.setText(self.tr("Choose color"))
        self.choiceLabel.setText(self.buttonGroup.checkedButton().text())
        self.card.titleLabel.setText(self.tr("Theme Color"))
        self.card.contentLabel.setText(self.tr("Change the theme color of the interface"))
