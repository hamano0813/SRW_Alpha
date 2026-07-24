#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional

import win32clipboard
from PySide6.QtCore import (Qt, QAbstractTableModel, QSortFilterProxyModel, QModelIndex, QEvent, QRegularExpression,
                            Signal)
from PySide6.QtGui import QMouseEvent, QCursor, QAction, QKeyEvent, QFont
from PySide6.QtWidgets import (QTableView, QPushButton, QVBoxLayout, QFrame, QHBoxLayout, QAbstractButton,
                               QStyleOptionHeader, QWidget, QStyle, QStylePainter, QMenu, QLineEdit)

from structure.generic import SEQUENCE
from widget import ArrayTable, FontLabel
from widget.abstract_widget import ControlWidget, AbstractWidget
from widget.command.command_dialog import CommandDialog, CommandExplain
from widget.command_search import CommandSearch


class StageModel(QAbstractTableModel):
    def __init__(self, parent, **kwargs):
        super(StageModel, self).__init__(parent)
        self.commands: list[dict[str, int | str]] = list()
        self.columns = ('指令释义',)
        self.explain = CommandExplain(**kwargs)

    def install(self, commands: SEQUENCE) -> bool:
        self.beginResetModel()
        self.commands = commands
        self.endResetModel()
        return True

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> any:
        if role != Qt.DisplayRole:
            return None
        elif orientation == Qt.Horizontal:
            return self.columns[section]
        return f'{self.commands[section]["Pos"]:04X}'

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.commands)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 1

    def data(self, index: QModelIndex, role: int = ...) -> any:
        command = self.commands[index.row()]
        if role == Qt.DisplayRole:
            return self.explain.explain(command).replace('\n', '')
        if role == Qt.ToolTipRole:
            return f"指令 步長 參數\n" \
                   f"{command['Code']:02X}    {command['Count']:02X}    " \
                   f"{' '.join(list(map(lambda x: f'{x:04X}', command['Param'])))}"
        if role == Qt.FontRole:
            font = QFont()
            font.setFamilies(['Consolas', 'Yu Gothic UI', 'Wingdings'])
            font.setPointSize(14)
            if command['Code'] <= 0x01:
                font.setBold(True)
                font.setLetterSpacing(QFont.PercentageSpacing, 200)
            if command['Code'] in (0x08, 0x09, 0x0A):
                font.setUnderline(True)
            if command['Code'] in range(0x02, 0x08):
                font.setItalic(True)
            return font
        return None

    def flags(self, index: QModelIndex) -> Optional[Qt.ItemFlags]:
        if not index.isValid():
            return None
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def find_target(self, pos: int) -> Optional[int]:
        for idx, command in enumerate(self.commands):
            if command['Pos'] == pos:
                return idx
        return None

    def find_start(self, end_row: int) -> Optional[int]:
        for row in range(end_row, 1, -1):
            if self.commands[row - 1]['Code'] in (0x01, 0x0A):
                pos = self.commands[row]['Pos']
                for idx, command in enumerate(self.commands):
                    if command['Code'] in (0x08, 0x09):
                        if command['Param'][0] == pos:
                            return idx
        return None

    def insert_command(self, row: int, command: dict[str, int | str | list]) -> None:
        self.beginInsertRows(QModelIndex(), row, row)
        command['Pos'] = self.commands[row]['Pos']
        for idx, _command in enumerate(self.commands):
            if idx >= row:
                _command['Pos'] += command['Count']
            if (_command['Code'] in (0x08, 0x09)) and (_command['Param'][0] > command['Pos']):
                _command['Param'][0] += command['Count']
        self.commands.insert(row, command)
        self.endInsertRows()

    def remove_command(self, row: int) -> None:
        self.beginRemoveRows(QModelIndex(), row, row)
        command = self.commands.pop(row)
        for idx, _command in enumerate(self.commands):
            if idx >= row:
                _command['Pos'] -= command['Count']
            if (_command['Code'] in (0x08, 0x09)) and (_command['Param'][0] > command['Pos']):
                _command['Param'][0] -= command['Count']
        self.endRemoveRows()

    def update_command(self, row: int, command: dict[str, int | str | list]) -> None:
        self.remove_command(row)
        self.insert_command(row, command)


class StageTable(QTableView, ControlWidget):
    def __init__(self, parent, data_name, **kwargs):
        QTableView.__init__(self, parent=None)
        ControlWidget.__init__(self, parent, data_name, **kwargs)
        self.jump_indexes: list[QModelIndex] = list()

        self.setWordWrap(True)

        self.horizontalHeader().setProperty('language', 'zh')
        self.verticalHeader().setFixedWidth(40)
        self.verticalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # noinspection PyUnresolvedReferences
        self.customContextMenuRequested.connect(self.right_menu)

        if corner := self.kwargs.get('corner', False):
            self.set_corner(corner)

    def install(self, data_set: dict[str, int | str | SEQUENCE]) -> bool:
        model = StageModel(self, **self.kwargs)
        model.install(data_set.get(self.data_name, list()))
        proxy = QSortFilterProxyModel(self)
        proxy.setSourceModel(model)
        self.setModel(proxy)
        self.horizontalHeader().setSectionResizeMode(0, self.horizontalHeader().Stretch)

        self.data_set = data_set

        # noinspection PyUnresolvedReferences
        self.clicked[QModelIndex].connect(self.select_index)
        # noinspection PyUnresolvedReferences
        self.selectionModel().currentChanged[QModelIndex, QModelIndex].connect(self.select_index)
        self.jump_indexes: list[QModelIndex] = list()
        return True

    def jump_pos(self, pos: int):
        positions = [command['Pos'] for command in self.model().sourceModel().commands]
        if pos in positions:
            target = self.model().sourceModel().createIndex(positions.index(pos), 0)
            self.scrollTo(target, self.PositionAtCenter)
            self.setCurrentIndex(self.model().mapFromSource(target))

    def select_index(self, index: QModelIndex) -> bool:
        if not index.isValid():
            return False
        self.control_child(self.model().mapToSource(index).row())
        return True

    def insert_command(self) -> bool:
        if not self.selectedIndexes():
            row = self.model().sourceModel().rowCount()
        else:
            row = self.model().mapToSource(self.selectedIndexes()[0]).row()
        if command := CommandDialog(self, **self.kwargs).get_command():
            self.model().sourceModel().insert_command(row, command)
            self.resizeRowsToContents()
            return True
        return False

    def remove_command(self) -> bool:
        if not self.selectedIndexes():
            return False
        row_set = set(map(lambda index: self.model().mapToSource(index).row(), self.selectedIndexes()))
        for row in row_set:
            self.model().sourceModel().remove_command(row)
        self.resizeRowsToContents()
        return True

    def update_command(self) -> bool:
        if not self.selectedIndexes():
            return False
        row = self.model().mapToSource(self.selectedIndexes()[0]).row()
        if command := CommandDialog(self, self.model().sourceModel().commands[row], **self.kwargs).get_command():
            self.model().sourceModel().update_command(row, command)
            self.resizeRowsToContents()
            return True
        return False

    def right_menu(self) -> None:
        right_click_menu = QMenu()
        right_click_menu.setProperty('language', 'zh')
        copy_action = QAction('复制(C)', self)
        copy_action.triggered.connect(self.copy_range)
        right_click_menu.addActions([copy_action])
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
        text = '\r\n'.join([f'"{t}"' if '\n' in t else t for t in ['\t'.join(row) for row in data]])
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        return True

    def back_jump(self) -> bool:
        if self.jump_indexes:
            target = self.model().mapFromSource(self.jump_indexes.pop(-1))
            self.scrollTo(target, self.PositionAtCenter)
            self.setCurrentIndex(target)
            return True
        return False

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        index = self.model().mapToSource(self.indexAt(event.pos()))
        text: str = index.data(Qt.DisplayRole)
        if text.startswith('GOTO') or text.startswith('RUN'):
            pos = int(text.split(' ')[-1], 16)
            if row := self.model().sourceModel().find_target(pos):
                target: QModelIndex = self.model().mapFromSource(self.model().sourceModel().createIndex(row, 0))
                self.scrollTo(target, self.PositionAtCenter)
                self.setCurrentIndex(target)
                return self.jump_indexes.append(index)
        if text == 'BACK':
            if row := self.model().sourceModel().find_start(index.row()):
                target: QModelIndex = self.model().mapFromSource(self.model().sourceModel().createIndex(row, 0))
                self.scrollTo(target, self.PositionAtCenter)
                self.setCurrentIndex(target)
                return self.jump_indexes.append(index)
        self.update_command()
        return super(StageTable, self).mouseDoubleClickEvent(event)

    def keyPressEvent(self, event: QKeyEvent) -> bool:
        if event.key() == Qt.Key_C and event.modifiers() == Qt.ControlModifier:
            return self.copy_range()
        if event.key() == Qt.Key_Backspace:
            return self.back_jump()
        super(StageTable, self).keyPressEvent(event)
        return True

    def set_corner(self, text: str) -> None:
        # noinspection PyTypeChecker
        corner_button: QAbstractButton = self.findChild(QAbstractButton)
        corner_button.setText(text)
        corner_button.setObjectName('Corner')
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
        self.resizeRowsToContents()


class StageFrame(QFrame, AbstractWidget):
    jumpSearch = Signal(int, int)

    def __init__(self, parent, data_name: str, **kwargs):
        QFrame.__init__(self, parent)
        AbstractWidget.__init__(self, parent, data_name, **kwargs)
        self._parent: ArrayTable | QWidget = parent

        self.table = StageTable(parent, data_name, **kwargs)

        left_layout = QVBoxLayout()
        filter_layout = QHBoxLayout()
        filter_label = FontLabel('查询过滤')
        self.filter_line = QLineEdit()
        # noinspection PyUnresolvedReferences
        self.filter_line.textChanged[str].connect(self.table.filterChanged)
        self.filter_line.setProperty('language', 'zh')
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_line)
        left_layout.addWidget(self.table)
        left_layout.addLayout(filter_layout)

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(self.init_buttons())
        self.setLayout(main_layout)

    # noinspection PyUnresolvedReferences
    def init_buttons(self) -> QVBoxLayout:
        edit_button = QPushButton('编辑指令')
        insert_button = QPushButton('插入指令')
        delete_button = QPushButton('删除指令')
        search_button = QPushButton('全局查找')
        edit_button.setProperty('language', 'zhb')
        insert_button.setProperty('language', 'zhb')
        delete_button.setProperty('language', 'zhb')
        search_button.setProperty('language', 'zhb')
        edit_button.clicked.connect(self.table.update_command)
        insert_button.clicked.connect(self.table.insert_command)
        delete_button.clicked.connect(self.table.remove_command)
        search_button.clicked.connect(self.search_command)
        button_layout = QVBoxLayout()
        button_layout.addWidget(edit_button)
        button_layout.addWidget(insert_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(search_button)
        button_layout.addStretch()
        return button_layout

    def install(self, data_set: dict[str, int | str | SEQUENCE]) -> bool:
        if data_set:
            self.filter_line.clear()
            self.table.scrollToTop()
        return self.table.install(data_set)

    def search_command(self):
        scenario_data = self._parent.data_set
        search = CommandSearch(self, Qt.Dialog, scenario_data, explain=self.table.model().sourceModel().explain)
        search.jumpSearch[int, int].connect(self.jumpSearch)
        search.show()
