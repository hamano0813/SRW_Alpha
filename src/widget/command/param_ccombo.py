#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QCheckBox, QLineEdit, QListWidget, QListWidgetItem

from widget.command.param_widget import ParamWidget


class ParamCCombo(QComboBox, ParamWidget):
    def __init__(self, name, default, item: list[str], **kwargs):
        QComboBox.__init__(self, parent=None)
        ParamWidget.__init__(self, name, default, **kwargs)
        self.item = item
        self.dummy = kwargs.get('dummy', '')
        self.sep = kwargs.get('sep', ' ')
        self.setLineEdit(QLineEdit())
        self.lineEdit().setReadOnly(True)
        self.check_list: list[QCheckBox] = list()
        self.init_check()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

    def init_check(self) -> None:
        list_widget = QListWidget()
        for item in self.item:
            check_box = QCheckBox(item)
            self.check_list.append(check_box)
            check_item = QListWidgetItem(list_widget)
            list_widget.setItemWidget(check_item, check_box)
        self.setModel(list_widget.model())
        self.setView(list_widget)

    def install(self, param: int = None) -> None:
        if param is not None:
            for bit, check_box in enumerate(self.check_list):
                check_box.disconnect(check_box)
                check_box.setChecked((param & 1 << bit) >> bit)
                # noinspection PyUnresolvedReferences
                check_box.stateChanged.connect(self.set_text)
            return self.lineEdit().setText(self.explain(param))
        for bit, check_box in enumerate(self.check_list):
            check_box.disconnect(check_box)
            check_box.setChecked((self.default & 1 << bit) >> bit)
            # noinspection PyUnresolvedReferences
            check_box.stateChanged.connect(self.set_text)
        return self.lineEdit().setText(self.explain(self.default))

    def data(self) -> int:
        value = 0
        for bit, check in enumerate(self.check_list):
            if check.isChecked():
                value |= (1 << bit)
        return value

    def explain(self, param: int) -> str:
        texts = []
        for bit, item_text in enumerate(self.item):
            texts.append(item_text) if (param & 1 << bit) else texts.append(self.dummy)
        while '' in texts:
            texts.remove('')
        return self.sep.join(texts)

    def new(self) -> Optional["ParamCCombo"]:
        return self.__class__(self.name, self.default, self.item, **self.kwargs)

    def set_text(self) -> None:
        self.lineEdit().setText(self.explain(self.data()))
        self.data_change()
