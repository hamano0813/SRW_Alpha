#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import QSpinBox

from structure.generic import Value
from widget.abstract_widget import SingleWidget


class ValueSpin(SingleWidget, QSpinBox):
    def __init__(self, parent, data_name: str, structure: Value, **kwargs):
        QSpinBox.__init__(self, parent)
        SingleWidget.__init__(self, parent, data_name, structure, **kwargs)
        self.multiple = self.kwargs.get('multiple', 1)
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
        if self.structure.bit is not None:
            if isinstance(self.structure.bit, int):
                minimum = 0
                maximum = 1
            else:
                minimum = 0
                if isinstance(self.structure, int):
                    maximum = 2
                else:
                    maximum = (1 << (self.structure.bit[1] - self.structure.bit[0]))
        maximum -= 1
        minimum *= self.multiple
        maximum *= self.multiple
        self.setSingleStep(self.multiple)
        self.setRange(minimum, maximum)
        self.lineEdit().setValidator(QIntValidator(minimum, maximum))
        return True

    def textFromValue(self, value: int) -> str:
        if self.structure.length < 0:
            return f'{value:+d}'
        return str(value)

    def valueFromText(self, text: str) -> int:
        if text:
            return int(text)
        return self.value()

    def install(self, data_set: dict[str, int | str], delegate: bool = False) -> bool:
        self.disconnect(self)
        self.data_set = data_set
        value = self.data_set.get(self.data_name, 0)
        self.setValue(value * self.multiple)
        if not delegate:
            # noinspection PyUnresolvedReferences
            self.valueChanged.connect(self.overwrite)
        return True

    def display(self, value: int) -> str:
        return self.textFromValue(value * self.multiple) + '   '

    def interpret(self, text: str) -> int:
        return self.valueFromText(text) // self.multiple

    def delegate(self) -> int:
        return self.value() // self.multiple

    def new(self, parent):
        return self.__class__(parent, self.data_name, self.structure, wheel=True, **self.kwargs)
