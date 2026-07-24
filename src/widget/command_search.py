#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal
from PySide6.QtGui import QMouseEvent, QFont
from PySide6.QtWidgets import QDialog, QComboBox, QTableView, QLabel, QPushButton, QVBoxLayout, QGridLayout

from widget.command.command_dialog import CommandExplain
from widget.command.param_widget import ParamWidget


class SearchModel(QAbstractTableModel):
    def __init__(self):
        super(SearchModel, self).__init__(parent=None)
        self.result = tuple()
        self.columns = ('场景序号', '  索引  ', '释义')

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if role != Qt.DisplayRole:
            return None
        elif orientation == Qt.Horizontal:
            return self.columns[section]
        return section + 1

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.result)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 3

    def data(self, index: QModelIndex, role: int = ...) -> any:
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            data = self.result[index.row()][index.column()]
            if index.column() == 0:
                return f'[{data:02X}]'
            if index.column() == 1:
                return f'{data:04X}'
            return data.replace('\n', '')
        if role == Qt.TextAlignmentRole:
            if index.column() < 2:
                return int(Qt.AlignCenter)
        if role == Qt.FontRole:
            font = QFont()
            font.setFamilies(['Consolas', 'Yu Gothic UI', 'Wingdings'])
            font.setPointSize(12)
            if index.column() < 2:
                font.setBold(True)
            return font
        return None

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return None
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def set_result(self, result: list):
        self.beginResetModel()
        self.result = result
        self.endResetModel()


class SearchTable(QTableView):
    doubleClick = Signal(int, int)

    def __init__(self):
        super(SearchTable, self).__init__(parent=None)
        self.setModel(SearchModel())

        self.setSelectionBehavior(QTableView.SelectRows)
        self.resizeColumnsToContents()
        self.horizontalHeader().setSectionResizeMode(2, self.horizontalHeader().Stretch)
        self.horizontalHeader().setProperty('language', 'zh')
        self.verticalHeader().hide()

    def set_result(self, result: list):
        self.model().set_result(result)
        # self.resizeRowsToContents()

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:
        index = self.indexAt(event.pos())
        scenario, pos, *_ = self.model().result[index.row()]
        # noinspection PyUnresolvedReferences
        self.doubleClick.emit(scenario, pos)


class CommandSearch(QDialog):
    jumpSearch = Signal(int, int)

    def __init__(self, parent, f, scenario_data, explain: CommandExplain):
        super(CommandSearch, self).__init__(parent, f)
        self.scenario_data: list[dict[str, int | list]] = scenario_data.get('场景设计')
        self.explain = explain

        self.position: tuple[int, int] = tuple()

        self.code_combo = self.init_command()
        self.code_combo.setProperty('language', 'zhb')
        self.robot_combo: QComboBox | ParamWidget = self.explain.w['机体'].new()
        self.robot_combo.insertItem(0, '一一', 0xFFFF)
        self.robot_combo.setCurrentIndex(0)
        self.pilot_combo: QComboBox | ParamWidget = self.explain.w['机师'].new()
        self.pilot_combo.insertItem(0, '一一', 0xFFFF)
        self.pilot_combo.setCurrentIndex(0)
        self.event_combo: QComboBox | ParamWidget = self.explain.w['事件'].new()
        self.event_combo.insertItem(0, '一一', 0xFFFF)
        self.event_combo.setCurrentIndex(0)

        search_button = QPushButton('查询')
        search_button.setFixedSize(72, 72)
        search_button.setProperty('language', 'zhb')
        # noinspection PyUnresolvedReferences
        search_button.clicked.connect(self.search_command)

        self.search_table = SearchTable()
        self.search_table.doubleClick[int, int].connect(self.get_position)

        code_label = QLabel('指令')
        code_label.setProperty('language', 'zhb')
        robot_label = QLabel('机体')
        robot_label.setProperty('language', 'zhb')
        pilot_label = QLabel('机师')
        pilot_label.setProperty('language', 'zhb')
        event_label = QLabel('事件')
        event_label.setProperty('language', 'zhb')

        option_layout = QGridLayout()
        option_layout.addWidget(code_label, 0, 0, 1, 1)
        option_layout.addWidget(self.code_combo, 0, 1, 1, 1)
        option_layout.addWidget(robot_label, 0, 2, 1, 1)
        option_layout.addWidget(self.robot_combo, 0, 3, 1, 1)
        option_layout.addWidget(pilot_label, 0, 4, 1, 1)
        option_layout.addWidget(self.pilot_combo, 0, 5, 1, 1)
        option_layout.addWidget(event_label, 1, 0, 1, 1)
        option_layout.addWidget(self.event_combo, 1, 1, 1, 5)
        option_layout.addWidget(search_button, 0, 6, 2, 1)

        main_layout = QVBoxLayout()
        main_layout.addLayout(option_layout)
        main_layout.addWidget(self.search_table)

        self.setLayout(main_layout)
        self.setWindowTitle('全局查找')
        self.setFixedHeight(600)

    def init_command(self):
        combo = QComboBox()
        combo.addItem('一', 0xFF)
        for code, settings in self.explain.settings.items():
            combo.addItem(settings[2], code)
        return combo

    def search_command(self):
        code = self.code_combo.currentData()
        robot = self.robot_combo.currentData()
        pilot = self.pilot_combo.currentData()
        event = self.event_combo.currentData()
        if all((code == 0xFF, robot == 0xFFFF, pilot == 0xFFFF, event == 0xFFFF)):
            self.search_table.set_result([])
            return
        result = list()
        for sid, scenario in enumerate(self.scenario_data):
            for command in scenario.get('Commands', list()):
                filter_result = self.filter_command(command, code, robot, pilot, event)
                if filter_result:
                    pos = command.get('Pos')
                    explain = self.explain.explain(command)
                    result.append((sid, pos, explain))
        self.search_table.set_result(result)

    def filter_command(self, command: dict, code: int, robot: int, pilot: int, event: int) -> bool:
        _code = [command.get('Code'), 0xFF]
        if _code[0] in (0x17, 0x18):
            return False

        _robot = [0xFFFF]
        _pilot = [0xFFFF]
        _event = [0xFFFF]

        widgets = self.explain.settings.get(_code[0])[1]
        for wid, widget in enumerate(widgets):
            if widget.name == self.robot_combo.name:
                _robot.append(command.get('Param')[wid])
            if widget.name == self.pilot_combo.name:
                _pilot.append(command.get('Param')[wid])
            if widget.name == self.event_combo.name:
                _event.append(command.get('Param')[wid])

        code_filter = True if code in _code else False
        robot_filter = True if robot in _robot else False
        pilot_filter = True if pilot in _pilot else False
        event_filter = True if event in _event else False

        if all((code_filter, robot_filter, pilot_filter, event_filter)):
            return True
        return False

    def get_position(self, scenario: int, pos: int):
        # noinspection PyUnresolvedReferences
        self.jumpSearch.emit(scenario, pos)
