#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque
from typing import Optional

import win32clipboard
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QAction, QCursor, QKeyEvent
from PySide6.QtWidgets import QWidget, QTableView, QMenu, QStyledItemDelegate, QStyleOptionViewItem

from structure.generic import SEQUENCE
from widget.abstract_widget import ControlWidget, SingleWidget


class TransposeModel(QAbstractTableModel):
    def __init__(self, parent: Optional['TransposeTable'], rows: dict[str, SingleWidget]):
        super(TransposeModel, self).__init__(parent)
        self.data_sequence: SEQUENCE = list()
        self.rows = rows
        self.history = list()
        self.history = deque(maxlen=100)

    def install(self, data_sequence: SEQUENCE) -> bool:
        self.beginResetModel()
        self.data_sequence = data_sequence
        self.endResetModel()
        return True

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if role != Qt.DisplayRole:
            return None
        elif orientation == Qt.Horizontal:
            return section
        return tuple(self.rows.keys())[section]

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.rows)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self.data_sequence)

    def data(self, index: QModelIndex, role: int = ...) -> any:
        row_name = tuple(self.rows.keys())[index.row()]
        data = self.data_sequence[index.column()][row_name]
        if role == Qt.DisplayRole:
            return self.rows[row_name].display(data)
        if role == Qt.TextAlignmentRole:
            return int(self.rows[row_name].kwargs.get('alignment', Qt.AlignLeft) | Qt.AlignVCenter)
        if role == Qt.EditRole:
            return data
        if role == Qt.UserRole:
            return self.data_sequence[index.column()], self.rows[row_name]
        if role == Qt.FontRole:
            if font := self.rows[row_name].kwargs.get('font'):
                return font
        return None

    def setData(self, index: QModelIndex, data: int | str, role: int = ...) -> bool:
        if not index.isValid():
            return False
        row_name = tuple(self.rows.keys())[index.row()]
        previos_data = self.data_sequence[index.column()][row_name]
        if role == Qt.EditRole:
            _data = self.data_sequence[index.column()][row_name] = data
            if not _data == previos_data:
                self.history.append((index, previos_data))
            return True
        if role == Qt.UserRole:
            _data = self.data_sequence[index.column()][row_name] = self.rows[row_name].interpret(data)
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
            row_name = tuple(self.rows.keys())[index.row()]
            self.data_sequence[index.column()][row_name] = data


class TransposeDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super(TransposeDelegate, self).__init__(parent)

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


class TransposeTable(ControlWidget, QTableView):
    def __init__(self, parent, data_name, rows: dict[str, SingleWidget | QWidget], **kwargs):
        QTableView.__init__(self, parent=None)
        ControlWidget.__init__(self, parent, data_name, **kwargs)
        self.rows = rows
        self.setItemDelegate(TransposeDelegate(self))
        self.horizontalHeader().setHidden(True)
        self.verticalHeader().setProperty('language', 'zh')
        self.verticalHeader().setMinimumWidth(40)
        self.check_kwargs()

    def install(self, data_set: dict[str, int | str | SEQUENCE]) -> bool:
        transpose_model = TransposeModel(self, self.rows)
        transpose_model.install(data_set.get(self.data_name, list()))
        self.setModel(transpose_model)
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        for column in range(transpose_model.columnCount()):
            self.horizontalHeader().setSectionResizeMode(column, self.horizontalHeader().Stretch)
        return True

    def check_kwargs(self):
        if self.kwargs.get('single', False):
            self.setSelectionMode(QTableView.SingleSelection)
            self.setSelectionBehavior(QTableView.SelectColumns)
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
                self.model().undo()
                self.reset()
                return True
        super(TransposeTable, self).keyPressEvent(event)
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
                self.model().setData(index, text.strip(), Qt.UserRole)
        self.reset()
        return True
