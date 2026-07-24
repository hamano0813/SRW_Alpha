#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPlainTextEdit

from structure.generic import Text
from widget.abstract_widget import SingleWidget


class TextMulti(SingleWidget, QPlainTextEdit):
    def __init__(self, parent, data_name, structure: Text, extra: dict[str, str] = None, **kwargs):
        QPlainTextEdit.__init__(self, parent)
        SingleWidget.__init__(self, parent, data_name, structure, **kwargs)
        if extra:
            self.structure.extra |= extra
        if font := self.kwargs.get('font'):
            self.setFont(font)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

    def install(self, data_set: dict[str, int | str], delegate: bool = False) -> bool:
        self.disconnect(self)
        self.data_set = data_set
        text = self.data_set.get(self.data_name)
        self.setPlainText(self.display(text))
        if not delegate:
            # noinspection PyUnresolvedReferences
            self.editingFinished.connect(self.overwrite)
        return True

    def display(self, text: str) -> str:
        if text is not None:
            return text
        return ''

    def interpret(self, text: str) -> str:
        return text.rstrip()

    def delegate(self):
        return self.interpret(self.toPlainText())
