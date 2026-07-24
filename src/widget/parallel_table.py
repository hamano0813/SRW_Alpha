#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque
from typing import Optional

import win32clipboard
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QKeyEvent, QAction, QCursor
from PySide6.QtWidgets import QWidget, QTableView, QStyledItemDelegate, QStyleOptionViewItem, QMenu

from structure.generic import SEQUENCE
from widget.abstract_widget import ControlWidget, SingleWidget


class ParallelModel(QAbstractTableModel):
    def __init__(self, parent: Optional['ParallelTable'], columns: dict[str, SingleWidget]):
        super(ParallelModel, self).__init__(parent)
        self.data_list: list[SEQUENCE] = list()
        self.columns = columns
        self.history = list()
        self.history = deque(maxlen=100)

    def install(self, data_list: list[SEQUENCE]) -> bool:
        self.beginResetModel()
        self.data_list = data_list
        self.endResetModel()
        return True

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if role != Qt.DisplayRole:
            return None
        elif orientation == Qt.Horizontal:
            return tuple(self.columns.keys())[section]
        return section

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.data_list[0])

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self.columns)

    def data(self, index: QModelIndex, role: int = ...) -> any:
        column_name = tuple(self.columns.keys())[index.column()]
        data = self.data_list[index.column()][index.row()][column_name]
        if role == Qt.DisplayRole:
            return self.columns[column_name].display(data)
        if role == Qt.TextAlignmentRole:
            return int(self.columns[column_name].kwargs.get('alignment', Qt.AlignLeft) | Qt.AlignVCenter)
        if role == Qt.EditRole:
            return data
        if role == Qt.UserRole:
            return self.data_list[index.column()][index.row()], self.columns[column_name]
        if role == Qt.FontRole:
            if font := self.columns[column_name].kwargs.get('font'):
                return font
        return None

    def setData(self, index: QModelIndex, data: int | str, role: int = ...) -> bool:
        if not index.isValid():
            return False
        column_name = tuple(self.columns.keys())[index.column()]
        previos_data = self.data_list[index.column()][index.row()][column_name]
        if role == Qt.EditRole:
            _data = self.data_list[index.column()][index.row()][column_name] = data
            if not _data == previos_data:
                self.history.append((index, previos_data))
            return True
        if role == Qt.UserRole:
            _data = self.data_list[index.column()][index.row()][column_name] = self.columns[column_name].interpret(data)
            if not _data == previos_data:
                self.history.append((index, previos_data))
            return True
        return False

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return None
        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def undo(self):
        if self.history:
            index, data = self.history.pop()
            column_name = tuple(self.columns.keys())[index.column()]
            self.data_list[index.column()][index.row()][column_name] = data


class ParallelDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super(ParallelDelegate, self).__init__(parent)

    def createEditor(self, parent, option: QStyleOptionViewItem, index: QModelIndex) -> SingleWidget:
        editor = index.data(Qt.UserRole)[1].new(parent)
        return editor

    def setEditorData(self, editor: SingleWidget, index: QModelIndex) -> None:
        data_set = index.data(Qt.UserRole)[0]
        editor.install(data_set, True)

    def setModelData(self, editor: SingleWidget, model, index: QModelIndex) -> None:
        data = editor.delegate()
        model.setData(index, data, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index: QModelIndex):
        editor.setGeometry(option.rect.adjusted(-1, -1, 1, 1))


class ParallelTable(ControlWidget, QTableView):
    def __init__(self, parent, data_name: tuple, columns: dict[str, SingleWidget | QWidget], **kwargs):
        ControlWidget.__init__(self, parent, data_name, **kwargs)
        QTableView.__init__(self, parent)
        self.columns = columns
        self.setItemDelegate(ParallelDelegate(self))
        self.horizontalHeader().setProperty('orientation', 'horizontal')
        self.horizontalHeader().setProperty('language', 'zh')
        self.horizontalHeader().setMinimumSectionSize(70)
        self.verticalHeader().setHidden(True)

        self.check_kwargs()

    def install(self, data_set: dict[str, int | str | SEQUENCE]) -> bool:
        parallel_model = ParallelModel(self, self.columns)
        data_list: list[SEQUENCE] = [data_set.get(name, list()) for name in self.data_name]
        parallel_model.install(data_list)
        self.setModel(parallel_model)

        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        stretch_columns = self.kwargs.get('stretch', (0,))
        for column in stretch_columns:
            self.horizontalHeader().setSectionResizeMode(column, self.horizontalHeader().Stretch)
        return True

    def check_kwargs(self):
        if self.kwargs.get('copy', True):
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            # noinspection PyUnresolvedReferences
            self.customContextMenuRequested.connect(self.copy_paste)

    def keyPressEvent(self, event: QKeyEvent) -> bool:
        if self.kwargs.get('copy', True):
            if event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
                return self.copy_range()
            elif event.key() == Qt.Key_V and event.modifiers() == Qt.ControlModifier:
                return self.paste_range()
            elif event.key() == Qt.Key_Z and event.modifiers() == Qt.ControlModifier:
                self.model().sourceModel().undo()
                self.reset()
                return True
        super(ParallelTable, self).keyPressEvent(event)
        return True

    def copy_paste(self) -> None:
        right_click_menu = QMenu()
        right_click_menu.setProperty('language', 'zh')
        copy_action = QAction('复制(C)', self)
        copy_action.triggered.connect(self.copy_range)
        paste_action = QAction('粘贴(V)', self)
        paste_action.triggered.connect(self.paste_range)
        right_click_menu.addActions([copy_action, paste_action])
        right_click_menu.exec_(QCursor().pos())

    def copy_range(self) -> bool:
        if not self.selectedIndexes():
            return False
        indexes = self.selectedIndexes()
        row_set = set(map(lambda idx: idx.row(), indexes))
        col_set = set(map(lambda idx: idx.column(), indexes))
        row_count = max(row_set) - min(row_set) + 1
        col_count = max(col_set) - min(col_set) + 1
        data = [[''] * col_count for _ in range(row_count)]
        for index in indexes:
            data[index.row() - min(row_set)][index.column() - min(col_set)] = index.data(Qt.DisplayRole)
        text = '\r\n'.join([f'"{t}"' if '\n' in t else t for t in ['\t'.join(row) for row in data]])
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        return True

    def paste_range(self) -> bool:
        if not self.selectedIndexes():
            return False
        win32clipboard.OpenClipboard()
        text = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        if not text:
            return False
        data = [row.strip('"').split('\t') for row in text.strip().split('\r\n')]
        min_row = min(map(lambda idx: idx.row(), self.selectedIndexes()))
        min_col = min(map(lambda idx: idx.column(), self.selectedIndexes()))
        for rid, row in enumerate(data):
            for cid, text in enumerate(row):
                index = self.model().createIndex(min_row + rid, min_col + cid)
                self.model().sourceModel().setData(index, text.strip(), Qt.UserRole)
        self.reset()
        return True
