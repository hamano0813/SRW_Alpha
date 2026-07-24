#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtGui import QAction, QCursor, QKeyEvent
from PySide6.QtWidgets import QMenu

from structure.generic import SEQUENCE
from widget.array_table import ArrayModel, ArrayTable


class AiModel(ArrayModel):
    def __init__(self, parent, columns):
        super(AiModel, self).__init__(parent, columns)
        self.dummy = {'AI': 0x158, '目标机师': 0xFFFF, '目标X': 0xFF, '目标Y': 0xFF, '移动开始': 1, '生效': 1}

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.data_sequence) - 3

    def insertRow(self, row: int, parent: QModelIndex = QModelIndex()) -> bool:
        if len(self.data_sequence) in range(1, 0xA0):
            row_data = {k: 0 for k in self.data_sequence[-1].keys()} | self.dummy
            self.beginInsertRows(parent, row, row)
            self.data_sequence.insert(row, row_data)
            self.endInsertRows()
            return True
        return False

    def removeRow(self, row: int, parent: QModelIndex = QModelIndex()) -> bool:
        if self.data_sequence:
            self.beginRemoveRows(parent, row, row)
            self.data_sequence.pop(row)
            self.endRemoveRows()
            return True
        return False


class AiTable(ArrayTable):
    def __init__(self, parent, data_name, columns, **kwargs):
        super(AiTable, self).__init__(parent, data_name, columns, **kwargs)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.customContextMenuRequested.connect(self.right_menu)
        self.alignment = self.kwargs.get('alignment', Qt.AlignVCenter)
        self.horizontalHeader().setProperty('language', 'zh')

    def install(self, data_set: dict[str, int | str | SEQUENCE]) -> bool:
        array_model = AiModel(self, self.columns)
        array_model.install(data_set.get(self.data_name, list()))
        proxy = self.generate_proxy()
        proxy.setSourceModel(array_model)
        self.setModel(proxy)

        if self.kwargs.get('resizeColumns', True):
            self.resizeColumnsToContents()
        if self.kwargs.get('resizeRows', True):
            self.resizeRowsToContents()
        stretch_columns = self.kwargs.get('stretch', (0,))
        for column in stretch_columns:
            self.horizontalHeader().setSectionResizeMode(column, self.horizontalHeader().Stretch)
        self.data_set = data_set

        return True

    def keyPressEvent(self, event: QKeyEvent) -> bool:
        if self.kwargs.get('copy', True):
            if event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
                return self.copy_range()
            elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
                return self.paste_range()
            elif event.key() == Qt.Key_I and event.modifiers() == Qt.ControlModifier:
                return self.insert_row()
            elif event.key() == Qt.Key_D and event.modifiers() == Qt.ControlModifier:
                return self.remove_row()
            elif event.key() == Qt.Key_Z and event.modifiers() == Qt.ControlModifier:
                self.model().sourceModel().undo()
                self.reset()
                return True
        super(AiTable, self).keyPressEvent(event)
        return True

    def right_menu(self) -> None:
        right_click_menu = QMenu()
        right_click_menu.setProperty('language', 'zh')
        copy_action = QAction('复制(C)', self)
        copy_action.triggered.connect(self.copy_range)
        paste_action = QAction('粘贴(V)', self)
        paste_action.triggered.connect(self.paste_range)
        insert_action = QAction('插入(I)', self)
        insert_action.triggered.connect(self.insert_row)
        remove_action = QAction('刪除(D)', self)
        remove_action.triggered.connect(self.remove_row)
        right_click_menu.addActions([copy_action, paste_action, insert_action, remove_action])
        right_click_menu.exec_(QCursor().pos())

    def insert_row(self) -> bool:
        if not self.selectedIndexes():
            return False
        row = self.selectedIndexes()[0].row() + 1
        self.model().sourceModel().insertRow(row)
        return True

    def remove_row(self) -> bool:
        if not self.selectedIndexes():
            return False
        row = self.selectedIndexes()[0].row()
        self.model().sourceModel().removeRow(row)
        return True
