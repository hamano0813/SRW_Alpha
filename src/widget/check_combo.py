#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QCheckBox, QLineEdit, QListWidget, QListWidgetItem

from widget.abstract_widget import SingleWidget


class CheckCombo(SingleWidget, QComboBox):
    def __init__(self, parent, data_name, structure, item_list: list[str], **kwargs):
        SingleWidget.__init__(self, parent, data_name, structure, **kwargs)
        QComboBox.__init__(self, parent)
        self.item_list = item_list
        self.dummy = kwargs.get('dummy', '一')
        self.sep = kwargs.get('sep', ' ')
        self.setLineEdit(QLineEdit())
        self.lineEdit().setReadOnly(True)
        self.check_list: list[QCheckBox] = list()
        if font := self.kwargs.get('font'):
            self.lineEdit().setFont(font)
        self.init_check()
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

    def init_check(self):
        list_widget = QListWidget()
        for item in self.item_list:
            check_box = QCheckBox(item)
            check_box.setFont(self.kwargs.get('font')) if self.kwargs.get('font') else False
            self.check_list.append(check_box)
            check_item = QListWidgetItem(list_widget)
            list_widget.setItemWidget(check_item, check_box)
        self.setModel(list_widget.model())
        self.setView(list_widget)

    def install(self, data_set: dict[str, int | str], delegate: bool = False) -> bool:
        self.disconnect(self)
        self.data_set = data_set
        value = self.data_set.get(self.data_name, 0)
        for bit, check_box in enumerate(self.check_list):
            check_box.disconnect(check_box)
            check_box.setChecked((value & 1 << bit) >> bit)
            # noinspection PyUnresolvedReferences
            check_box.stateChanged.connect(self.overwrite)
        self.lineEdit().setText(self.value_text(value))
        # noinspection PyUnresolvedReferences
        self.lineEdit().textChanged.connect(self.overwrite)
        return True

    def overwrite(self) -> bool:
        value = 0
        for bit, check in enumerate(self.check_list):
            if check.isChecked():
                value |= (1 << bit)
        self.data_set[self.data_name] = value
        self.lineEdit().setText(self.value_text(value))
        return True

    def value_text(self, value: int) -> str:
        texts = []
        for bit, item_text in enumerate(self.item_list):
            texts.append(item_text) if (value & 1 << bit) else texts.append(self.dummy)
        while '' in texts:
            texts.remove('')
        return self.sep.join(texts)
