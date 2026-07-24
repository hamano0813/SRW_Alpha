#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QSpinBox

from structure.generic import Value
from widget.abstract_widget import SingleWidget


class HexSpin(SingleWidget, QSpinBox):
    def __init__(self, parent, data_name: str, structure: Value, **kwargs):
        QSpinBox.__init__(self, parent)
        SingleWidget.__init__(self, parent, data_name, structure, **kwargs)
        if alignment := self.kwargs.get('alignment', Qt.AlignRight):
            self.setAlignment(alignment)
        if font := self.kwargs.get('font'):
            self.setFont(font)
        self.init_range()
        if not self.kwargs.get('wheel', False):
            self.wheelEvent = lambda x: None
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

    def init_range(self) -> bool:
        if (length := self.structure.length) > 0:
            maximum = 0x100 ** length
        else:
            maximum = 0x100 ** abs(length) // 2
        minimum = maximum - 0x100 ** abs(length)
        maximum -= 1
        self.setRange(minimum, maximum)
        self.lineEdit().setValidator(QIntValidator(minimum, maximum))
        return True

    def textFromValue(self, value: int) -> str:
        return f'{value:04X}'

    def valueFromText(self, text: str) -> int:
        if text:
            return int(text, 16)
        return self.value()

    def install(self, data_set: dict[str, int | str], delegate: bool = False) -> bool:
        self.disconnect(self)
        self.data_set = data_set
        value = self.data_set.get(self.data_name, 0)
        self.setValue(value)
        if not delegate:
            # noinspection PyUnresolvedReferences
            self.valueChanged.connect(self.overwrite)
        return True

    def display(self, value: int) -> str:
        return self.textFromValue(value) + '   '

    def interpret(self, text: str) -> int:
        return self.valueFromText(text)

    def delegate(self) -> int:
        return self.value()

    def new(self, parent):
        return self.__class__(parent, self.data_name, self.structure, wheel=True, **self.kwargs)
