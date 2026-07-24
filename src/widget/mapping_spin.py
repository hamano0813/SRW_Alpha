#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSpinBox

from structure.generic import Value
from widget.abstract_widget import SingleWidget


class MappingSpin(SingleWidget, QSpinBox):
    def __init__(self, parent, data_name: str, structure: Value, mapping: dict[int, str], **kwargs):
        QSpinBox.__init__(self, parent)
        SingleWidget.__init__(self, parent, data_name, structure, **kwargs)
        self.mapping = mapping
        if alignment := self.kwargs.get('alignment', Qt.AlignRight):
            self.setAlignment(alignment)
        if font := self.kwargs.get('font'):
            self.setFont(font)
        if readonly := self.kwargs.get('readonly', False):
            self.lineEdit().setReadOnly(readonly)
        self.init_mapping()
        if not self.kwargs.get('wheel', False):
            self.wheelEvent = lambda x: None
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

    def init_mapping(self) -> bool:
        self.setRange(min(self.mapping), max(self.mapping))
        self.setWrapping(True)
        return True

    def textFromValue(self, value: int) -> str:
        return self.mapping.get(value, self.mapping.get(self.maximum()))

    def valueFromText(self, text: str) -> int:
        return {value: key for key, value in self.mapping.items()}.get(text, self.maximum())

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
        if self.value() in self.mapping:
            return self.value()
        return max(self.mapping.keys())

    def new(self, parent):
        return self.__class__(parent, self.data_name, self.structure, self.mapping, wheel=True, **self.kwargs)
