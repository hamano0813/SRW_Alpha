#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import deque
from typing import Optional

import win32clipboard
from PySide6.QtCore import Qt, QAbstractTableModel, QSortFilterProxyModel, QModelIndex, QRegularExpression, QEvent
from PySide6.QtGui import QAction, QCursor, QKeyEvent, QPainter
from PySide6.QtWidgets import (QApplication, QWidget, QTableView, QMenu, QAbstractButton, QStyle, QStylePainter,
                               QStyledItemDelegate, QStyleOptionViewItem, QStyleOptionHeader, QCheckBox,
                               QStyleOptionButton)

from structure.generic import SEQUENCE
from widget.abstract_widget import ControlWidget, SingleWidget


class ArrayModel(QAbstractTableModel):
    def __init__(self, parent: Optional['ArrayTable'], columns: dict[str, SingleWidget]):
        super(ArrayModel, self).__init__(parent)
        self.data_sequence: SEQUENCE = list()
        self.columns = columns
        self.history = deque(maxlen=100)
        self.check_column = self.parent().kwargs.get('check', tuple())

    def install(self, data_sequence: SEQUENCE) -> bool:
        self.beginResetModel()
        self.data_sequence = data_sequence
        self.endResetModel()
        return True

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if role != Qt.DisplayRole:
            return None
        elif orientation == Qt.Horizontal:
            return tuple(self.columns.keys())[section]
        return f'  [{section:0{len(hex(len(self.data_sequence) - 1)) - 2}X}]'

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.data_sequence)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self.columns)

    def data(self, index: QModelIndex, role: int = ...) -> any:
        column_name = tuple(self.columns.keys())[index.column()]
        data = self.data_sequence[index.row()].get(column_name, 0)
        if role == Qt.DisplayRole:
            return self.columns[column_name].display(data)
        if role == Qt.TextAlignmentRole:
            return int(self.columns[column_name].kwargs.get('alignment', Qt.AlignLeft) | self.parent().alignment)
        if role == Qt.EditRole:
            return data
        if role == Qt.UserRole:
            return self.data_sequence[index.row()], self.columns[column_name]
        if role == Qt.FontRole:
            if font := self.columns[column_name].kwargs.get('font'):
                return font
        return None

    def setData(self, index: QModelIndex, data: int | str, role: int = ...) -> bool:
        if not index.isValid():
            return False
        column_name = tuple(self.columns.keys())[index.column()]
        previos_data = self.data_sequence[index.row()][column_name]
        if role == Qt.EditRole:
            _data = self.data_sequence[index.row()][column_name] = data
            if not _data == previos_data:
                self.history.append((index, previos_data))
            return True
        if role == Qt.UserRole:
            _data = self.data_sequence[index.row()][column_name] = self.columns[column_name].interpret(data)
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
            self.data_sequence[index.row()][column_name] = data


class ArrayDelegate(QStyledItemDelegate):
    def __init__(self, parent):
        super(ArrayDelegate, self).__init__(parent)

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        if index.column() in index.model().sourceModel().check_column:
            checkbox_option = QStyleOptionButton()
            checkbox_option.rect = option.rect
            checkbox_option.rect.moveLeft(option.rect.x() + option.rect.width() // 2 - 8)
            checkbox_option.state = QStyle.State_Enabled | QStyle.State_Active
            if index.data(Qt.EditRole):
                checkbox_option.state |= QStyle.State_On
            else:
                checkbox_option.state |= QStyle.State_Off
            return QApplication.style().drawControl(QStyle.CE_CheckBox, checkbox_option, painter, QCheckBox())
        return super(ArrayDelegate, self).paint(painter, option, index)

    def editorEvent(self, event: QEvent, model: ArrayModel | QSortFilterProxyModel, option, index: QModelIndex):
        if event.type() == QEvent.MouseButtonPress and option.rect.contains(event.pos()):
            if index.column() in model.sourceModel().check_column:
                value = index.data(Qt.EditRole)
                value = False if value else True
                return model.sourceModel().setData(index, value, Qt.EditRole)
        return super(ArrayDelegate, self).editorEvent(event, model, option, index)

    def createEditor(self, parent, option: QStyleOptionViewItem, index: QModelIndex) -> Optional[SingleWidget]:
        if index.column() in index.model().sourceModel().check_column:
            return None
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


class ArrayTable(ControlWidget, QTableView):
    def __init__(self, parent, data_name, columns: dict[str, SingleWidget | QWidget], **kwargs):
        QTableView.__init__(self, parent=None)
        ControlWidget.__init__(self, parent, data_name, **kwargs)
        self.columns = columns
        self.setItemDelegate(ArrayDelegate(self))
        self.horizontalHeader().setProperty('orientation', 'horizontal')
        self.horizontalHeader().setProperty('language', 'zh')
        self.horizontalHeader().setMinimumSectionSize(70)

        self.check_kwargs()
        self.alignment = self.kwargs.get('alignment', Qt.AlignVCenter)

    def source(self):
        return self.model().sourceModel()

    def install(self, data_set: dict[str, int | str | SEQUENCE]) -> bool:
        array_model = ArrayModel(self, self.columns)
        array_model.install(data_set.get(self.data_name, list()))
        proxy = self.generate_proxy()
        proxy.setSourceModel(array_model)
        self.setModel(proxy)

        if self.kwargs.get('resizeColumns', True):
            self.resizeColumnsToContents()
        if self.kwargs.get('resizeRows', True):
            QApplication.processEvents()
            self.resizeRowsToContents()
        stretch_columns = self.kwargs.get('stretch', (0,))
        for column in stretch_columns:
            self.horizontalHeader().setSectionResizeMode(column, self.horizontalHeader().Stretch)

        self.data_set = data_set
        self.control_child(0)

        # noinspection PyUnresolvedReferences
        self.clicked[QModelIndex].connect(self.select_index)
        # noinspection PyUnresolvedReferences
        self.selectionModel().currentChanged[QModelIndex, QModelIndex].connect(self.select_index)
        return True

    def generate_proxy(self) -> QSortFilterProxyModel:
        proxy = QSortFilterProxyModel(self)
        if self.kwargs.get('sortable', True):
            proxy.setSortRole(Qt.EditRole)
            self.setSortingEnabled(True)
            self.horizontalHeader().setSortIndicatorClearable(True)
        if self.kwargs.get('editable', False):
            proxy.flags = lambda x: Qt.ItemIsEnabled | Qt.ItemIsSelectable
        return proxy

    def select_index(self, index: QModelIndex) -> bool:
        if not index.isValid():
            return False
        self.control_child(self.model().mapToSource(index).row())
        return True

    def check_kwargs(self):
        if self.kwargs.get('single', False):
            self.setSelectionMode(QTableView.SingleSelection)
            self.setSelectionBehavior(QTableView.SelectRows)
        if self.kwargs.get('copy', True):
            self.setContextMenuPolicy(Qt.CustomContextMenu)
            # noinspection PyUnresolvedReferences
            self.customContextMenuRequested.connect(self.right_menu)
        if corner := self.kwargs.get('corner', False):
            self.set_corner(corner)

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
        super(ArrayTable, self).keyPressEvent(event)
        return True

    def filterChanged(self, text: str) -> None:
        filter_text = text.strip()
        if filter_text:
            pattern = QRegularExpression.wildcardToRegularExpression(f'*{filter_text}*')
            regexp = QRegularExpression(pattern)
            options = regexp.patternOptions() | QRegularExpression.CaseInsensitiveOption
            regexp.setPatternOptions(options)
            self.model().setFilterRegularExpression(regexp)
        else:
            self.model().setFilterRegularExpression('')

    def right_menu(self) -> None:
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
        indexes = tuple(map(self.model().mapToSource, self.selectedIndexes()))
        row_set = set(map(lambda index: index.row(), indexes))
        col_set = set(map(lambda index: index.column(), indexes))
        row_count = max(row_set) - min(row_set) + 1
        col_count = max(col_set) - min(col_set) + 1
        data = [[''] * col_count for _ in range(row_count)]
        for idx in indexes:
            data[idx.row() - min(row_set)][idx.column() - min(col_set)] = idx.data(Qt.DisplayRole)
            QApplication.processEvents()
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
        internal_id = self.selectedIndexes()[0].internalId()
        data = [row.strip('"').split('\t') for row in text.strip().split('\r\n')]
        min_row = min(map(lambda idx: idx.row(), self.selectedIndexes()))
        min_col = min(map(lambda idx: idx.column(), self.selectedIndexes()))
        for rid, row in enumerate(data):
            for cid, text in enumerate(row):
                index = self.model().createIndex(min_row + rid, min_col + cid, internal_id)
                source_index = self.model().mapToSource(index)
                self.model().sourceModel().setData(source_index, text.strip(), Qt.UserRole)
        self.reset()
        return True

    def set_corner(self, text: str):
        # noinspection PyTypeChecker
        corner_button: QAbstractButton = self.findChild(QAbstractButton)
        corner_button.setText(text)
        corner_button.setObjectName('Corner')
        corner_button.setProperty('language', 'zh')
        corner_button.installEventFilter(self)
        option = QStyleOptionHeader()
        option.text = corner_button.text()

    def eventFilter(self, obj: QWidget, event: QEvent) -> bool:
        if event.type() != QEvent.Paint or not isinstance(obj, QAbstractButton):
            return False
        option: QStyleOptionHeader = QStyleOptionHeader()
        option.initFrom(obj)
        style_state = QStyle.State_None
        if obj.isEnabled():
            style_state |= QStyle.State_Enabled
        if obj.isActiveWindow():
            style_state |= QStyle.State_Active
        if obj.isDown():
            style_state |= QStyle.State_Sunken
        option.state = style_state
        option.rect = obj.rect()
        option.text = obj.text()
        option.position = QStyleOptionHeader.OnlyOneSection
        painter = QStylePainter(obj)
        painter.drawControl(QStyle.CE_Header, option)
        return True
