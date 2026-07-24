#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSpinBox

from widget.command.param_widget import ParamWidget


class ParamVSpin(QSpinBox, ParamWidget):
    INTEGER_BASE = {'d': 10, 'x': 16, 'b': 2}

    def __init__(self, name: str, default: int, display: str = 'd', **kwargs):
        QSpinBox.__init__(self, parent=None)
        ParamWidget.__init__(self, name, default, **kwargs)
        self.display = display
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.setContextMenuPolicy(Qt.NoContextMenu)
        # noinspection PyUnresolvedReferences
        self.valueChanged.connect(self.data_change)
        self.mapping = self.kwargs.get('mapping')
        self.setRange(*self.kwargs.get('range', (-0x8000, 0x7FFF)))
        self.setDisplayIntegerBase(self.INTEGER_BASE.get(display[-1].lower()))

    def textFromValue(self, val: int) -> str:
        return f'{val:{self.display}}'

    def valueFromText(self, text: str) -> int:
        if not text:
            return self.value()
        fmt = self.display.lower()
        if fmt.endswith('d'):
            return int(text)
        if fmt.endswith('x'):
            return int(text, 16)
        if fmt.endswith('b'):
            return int(text, 2)

    def install(self, param: int = None) -> None:
        if param is not None:
            if self.name == "敌方序号":
                return self.setValue(0x10000 + param)
            return self.setValue(param)
        return self.setValue(self.default)

    def data(self) -> int:
        if self.name == "敌方序号":
            return self.value() - 0x10000
        return self.value()

    def explain(self, param: int) -> str:
        if self.mapping:
            return self.mapping.get(param, self.textFromValue(param)).replace('\u3000', '')
        if self.name == "敌方序号":
            return self.textFromValue(0x10000 + param)
        return self.textFromValue(param)

    def new(self) -> Optional["ParamVSpin"]:
        return self.__class__(self.name, self.default, self.display, **self.kwargs)
