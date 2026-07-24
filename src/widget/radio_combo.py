#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QLineEdit

from structure.generic import Value
from widget.abstract_widget import SingleWidget


class RadioCombo(SingleWidget, QComboBox):
    def __init__(self, parent, data_name: str, structure: Value, mapping: dict[int, str], **kwargs):
        QComboBox.__init__(self, parent)
        SingleWidget.__init__(self, parent, data_name, structure, **kwargs)
        self.mapping = dict()
        self.setLineEdit(QLineEdit())
        self.lineEdit().setReadOnly(True)
        if font := self.kwargs.get('font'):
            self.setFont(font)
            self.lineEdit().setFont(font)
        self.init_mapping(mapping)
        if not self.kwargs.get('wheel', False):
            self.wheelEvent = lambda x: None
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

    def init_mapping(self, mapping: dict[int, str]):
        if mapping:
            self.disconnect(self)
            self.clear()
            self.mapping = mapping
            for data, text in self.mapping.items():
                self.addItem(text, data)

    def install(self, data_set: dict[str, int | str], delegate: bool = False) -> bool:
        self.disconnect(self)
        self.data_set = data_set
        value = self.data_set.get(self.data_name, 0)
        self.setCurrentIndex(list(self.mapping.keys()).index(value))
        if not delegate:
            # noinspection PyUnresolvedReferences
            self.currentIndexChanged.connect(self.overwrite)
        return True

    def display(self, value: int) -> str:
        return self.mapping.get(value, '')

    def interpret(self, text: str) -> int:
        mapping = {value: key for key, value in self.mapping.items()}
        return mapping.get(text, self.data_set.get(self.data_name, 0))

    def delegate(self) -> int:
        return self.interpret(self.currentText())

    def new(self, parent):
        return self.__class__(parent, self.data_name, self.structure, self.mapping, wheel=True, **self.kwargs)
