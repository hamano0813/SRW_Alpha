#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QCheckBox, QListWidget, QListWidgetItem

from widget.abstract_widget import SingleWidget


class CheckList(SingleWidget, QListWidget):
    def __init__(self, parent, data_name, structure, item_list: list[str], **kwargs):
        SingleWidget.__init__(self, parent, data_name, structure, **kwargs)
        QListWidget.__init__(self, parent)
        self.item_list = item_list
        self.check_list: list[QCheckBox] = []
        self.init_check()

    def init_check(self):
        for item in self.item_list:
            check_box = QCheckBox(item)
            if font := self.kwargs.get('font'):
                check_box.setFont(font)
            self.check_list.append(check_box)
            if item:
                check_item = QListWidgetItem(self)
                self.setItemWidget(check_item, check_box)

    def install(self, data_set: dict[str, int | str], delegate: bool = False) -> bool:
        self.data_set = data_set
        value = self.data_set.get(self.data_name, 0)
        for bit, check_box in enumerate(self.check_list):
            check_box.disconnect(check_box)
            check_box.setChecked((value & 1 << bit) >> bit)
            # noinspection PyUnresolvedReferences
            check_box.stateChanged.connect(self.overwrite)
        return True

    def overwrite(self) -> bool:
        value = 0
        for bit, check in enumerate(self.check_list):
            if check.isChecked():
                value |= (1 << bit)
        self.data_set[self.data_name] = value
        return True
