#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog, QFormLayout, QDialogButtonBox, QComboBox, QPushButton, QVBoxLayout,
                               QPlainTextEdit, QLabel, QApplication, QHBoxLayout)

from widget.command.command_explain import CommandExplain, EnumData
from widget.command.param_widget import ParamWidget


class CommandDialog(QDialog):
    def __init__(self, parent, command: dict = None, **kwargs):
        super(CommandDialog, self).__init__(parent, f=Qt.Dialog)
        self.setWindowTitle('编辑指令' if command else '插入指令')
        self.explain: CommandExplain = CommandExplain(**kwargs)
        self.widgets: list[ParamWidget] = list()

        self.code_combo = QComboBox()
        self.code_combo.setProperty('language', 'zhb')
        self.code_combo.setFixedWidth(560)
        for code, settings in self.explain.settings.items():
            self.code_combo.addItem(settings[2], code)

        self.explain_text = QPlainTextEdit()
        self.explain_text.setReadOnly(True)
        self.explain_text.setContextMenuPolicy(Qt.NoContextMenu)
        self.explain_text.setStyleSheet("* {font: 12pt bold 'Consolas', 'Yu Gothic UI semibold', 'Wingdings';}")
        self.explain_text.setFixedWidth(640)

        self.edit_layout = QFormLayout()

        left_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        label = QLabel('指令选择')
        label.setProperty('language', 'zhb')
        top_layout.addWidget(label)
        top_layout.addWidget(self.code_combo)
        left_layout.addLayout(top_layout)
        left_layout.addWidget(self.explain_text)

        right_layout = QVBoxLayout()
        right_layout.addLayout(self.edit_layout)
        right_layout.addStretch()
        right_layout.addWidget(self.init_button())

        main_layout = QHBoxLayout()
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)
        self.setLayout(main_layout)

        self.init_widgets(command)
        # noinspection PyUnresolvedReferences
        self.code_combo.currentIndexChanged.connect(self.reset_widgets)

    def get_command(self) -> dict[str, int | list[int]]:
        if self.exec():
            return self.command()

    def command(self) -> dict[str, int | list[int]]:
        command = {'Pos': 0, 'Code': 0, 'Count': 1, 'Param': list(), 'Data': ''}
        code = command['Code'] = self.code_combo.currentData()
        command['Param'] = [widget.data() for widget in self.widgets]
        if code == 0xB9:
            command['Count'] = command['Param'][0] * 4 + 5
        elif code == 0x64:
            command['Count'] = 2
        else:
            command['Count'] = len(command['Param']) + 1
        return command

    def explain_command(self) -> None:
        self.explain_text.setPlainText(self.explain.explain(self.command()))

    def init_widgets(self, command: dict = None) -> None:
        code = 0 if not command else command['Code']
        param = [1] if not command else command['Param']

        param_widgets: list[ParamWidget] = self.explain.settings.get(code)[1]
        self.code_combo.setCurrentIndex(list(self.explain.settings.keys()).index(code))

        for param_widget in param_widgets:
            widget: ParamWidget = param_widget.new()
            if widget.name == '无效参数':
                # noinspection PyUnresolvedReferences
                widget.setEnabled(False)
            label = QLabel(widget.name)
            label.setProperty('language', 'zhb')
            label.setFixedWidth(72)
            self.edit_layout.addRow(label, widget)
            self.widgets.append(widget)

        if code == 0x62:
            self.widgets[0].dataChanged[int].connect(self.adjust_62)
            self.adjust_62(param[0])

        if code == 0xB9:
            self.widgets[0].dataChanged[int].connect(self.adjust_b9)

        for idx, widget in enumerate(self.widgets):
            widget.install(param[idx])
            if idx > 0 or code != 0xB9:
                widget.dataChanged.connect(self.explain_command)

        self.explain_command()
        self.resize_self()

    def reset_widgets(self) -> None:
        for i in range(len(self.widgets)):
            self.edit_layout.removeRow(0)
        self.widgets = list()

        code = self.code_combo.currentData()
        param_widgets: list[ParamWidget] = self.explain.settings.get(code)[1]
        for param_widget in param_widgets:
            widget: ParamWidget = param_widget.new()
            if widget.name == '无效参数':
                # noinspection PyUnresolvedReferences
                widget.setEnabled(False)
            label = QLabel(widget.name)
            label.setProperty('language', 'zhb')
            label.setFixedWidth(72)
            self.edit_layout.addRow(label, widget)
            self.widgets.append(widget)

        if code == 0x62:
            self.widgets[0].dataChanged[int].connect(self.adjust_62)
            self.adjust_62(0)

        if code == 0xB9:
            self.widgets[0].dataChanged[int].connect(self.adjust_b9)

        for idx, widget in enumerate(self.widgets):
            widget.install()
            if idx > 0 or code != 0xB9:
                widget.dataChanged.connect(self.explain_command)

        self.explain_command()
        self.resize_self()

    def resize_self(self) -> None:
        QApplication.processEvents()
        self.resize(self.minimumSizeHint())

    # noinspection PyUnresolvedReferences
    def adjust_62(self, code: int = 0):
        self.widgets[1].init_mapping(EnumData.COMMAND['换装'][code])

    def adjust_b9(self, count: int) -> None:
        adjust_count = count - (len(self.widgets) // 4 - 1)
        if adjust_count < 0:
            for i in range(abs(adjust_count) * 4):
                self.edit_layout.removeRow(self.edit_layout.rowCount() - 1)
            self.widgets = self.widgets[:adjust_count * 4]
            self.resize_self()
        else:
            start_idx = len(self.widgets)
            for i in range(adjust_count):
                self.widgets.extend([w.new() for w in self.widgets[-4:]])
            for widget in self.widgets[start_idx:]:
                label = QLabel(widget.name)
                label.setProperty('language', 'zhb')
                self.edit_layout.addRow(label, widget)
                widget.dataChanged.connect(self.explain_command)
                widget.install()
        self.explain_command()

    # noinspection PyUnresolvedReferences
    def init_button(self) -> QDialogButtonBox:
        accept_button = QPushButton('确定')
        accept_button.setProperty('language', 'zhb')
        accept_button.setProperty('group', 'param')
        reject_button = QPushButton('取消')
        reject_button.setProperty('language', 'zhb')
        reject_button.setProperty('group', 'param')
        button_box = QDialogButtonBox()
        button_box.setOrientation(Qt.Horizontal)
        button_box.addButton(accept_button, QDialogButtonBox.AcceptRole)
        button_box.addButton(reject_button, QDialogButtonBox.RejectRole)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        return button_box
