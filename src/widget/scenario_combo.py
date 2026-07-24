#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, QEvent
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QTableView, QComboBox, QStyle, QStyleOptionComboBox, QStylePainter, QAbstractItemView, \
    QStyleOptionHeader, QAbstractButton, QWidget

from parameter import EnumData
from widget.abstract_widget import ControlWidget


class ScenarioModel(QAbstractTableModel):
    def __init__(self, parent, columns: tuple[str, str, str, str], scenario_data: dict[int, tuple[str, str, str, str]]):
        super(ScenarioModel, self).__init__(parent)
        self.columns = columns
        self.scenario_data = scenario_data

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if role != Qt.DisplayRole:
            return None
        elif orientation == Qt.Horizontal:
            return self.columns[section]
        return f'  [{section:0{len(hex(len(self.scenario_data) - 1)) - 2}X}]'

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.scenario_data)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self.columns)

    def data(self, index: QModelIndex, role: int = ...) -> any:
        if role == Qt.DisplayRole:
            return self.scenario_data[index.row()][index.column()]
        if role == Qt.TextAlignmentRole:
            if index.column() in (0, 1, 2,):
                return int(Qt.AlignHCenter | Qt.AlignVCenter)
            return int(Qt.AlignLeft | Qt.AlignVCenter)
        return None

    def flags(self, index: QModelIndex):
        if not index.isValid():
            return None
        if index.row() in (0x7E, 0x82, 0x83, 0x84, 0x85):
            return ~Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable


class ScenarioTable(ControlWidget, QTableView):
    def __init__(self, parent, **kwargs):
        QTableView.__init__(self, parent=None)
        ControlWidget.__init__(self, parent, data_name='', **kwargs)
        self.horizontalHeader().setProperty('orientation', 'horizontal')
        self.horizontalHeader().setProperty('language', 'zh')
        self.setSelectionMode(QTableView.SingleSelection)
        self.setSelectionBehavior(QTableView.SelectRows)
        self.set_corner(' 序号')

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


class ScenarioCombo(QComboBox):
    def __init__(self, parent):
        super(ScenarioCombo, self).__init__(parent)
        model = ScenarioModel(self, ('关卡代码', '路线', '话数', '标题'), EnumData.SCENARIO)
        view = ScenarioTable(self)

        self.setModel(model)
        self.setView(view)

        self.setMaxVisibleItems(20)
        self.setStyleSheet('* {font: 900 16pt;} QAbstractItemView::item {padding: 0 30px;}')
        self.init_view()

    def view(self) -> QAbstractItemView | ScenarioTable:
        return super(ScenarioCombo, self).view()

    def init_view(self):
        self.view().resizeColumnsToContents()
        self.view().resizeRowsToContents()
        # self.view().verticalHeader().setHidden(True)
        self.view().horizontalHeader().setSectionResizeMode(3, self.view().horizontalHeader().Stretch)

        self.view().setRowHidden(0x7E, True)
        self.view().setRowHidden(0x82, True)
        self.view().setRowHidden(0x83, True)
        self.view().setRowHidden(0x84, True)
        self.view().setRowHidden(0x85, True)

        # noinspection PyUnresolvedReferences
        self.currentIndexChanged.connect(self.select_index)
        self.select_index()

    def select_index(self):
        code, root, idx, name = self.model().scenario_data[self.currentIndex()]
        self.setPlaceholderText(f'{idx}\t\t{name}\t\t({root})')

    def paintEvent(self, event):
        painter = QStylePainter(self)
        painter.setPen(self.palette().color(QPalette.Text))
        opt = QStyleOptionComboBox()
        self.initStyleOption(opt)
        painter.drawComplexControl(QStyle.CC_ComboBox, opt)
        opt.palette.setBrush(QPalette.ButtonText, opt.palette.brush(QPalette.ButtonText).color().lighter())
        if self.placeholderText():
            opt.currentText = self.placeholderText()
        painter.drawControl(QStyle.CE_ComboBoxLabel, opt)
