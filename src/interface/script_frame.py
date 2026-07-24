#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import deepcopy
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout

from structure import ScriptBIN
from structure.generic import Value, Text
from widget import *


class ScriptFrame(BackgroundFrame):
    def __init__(self, parent=None, **kwargs):
        super(ScriptFrame, self).__init__(parent, **kwargs)
        self.rom: Optional[ScriptBIN] = None

        self.init_ui()

    def init_ui(self):
        script = self.init_script_table()

        self['剧本列表'] = ArrayTable(self, '剧本列表', {}, stretch=tuple())
        self['指令列表'] = ScriptTable(self['剧本列表'], '指令列表', {
            '指令码': HexSpin(None, '指令码', Value(0x0, 0x2), alignment=Qt.AlignRight),
            '参数一': HexSpin(None, '参数一', Value(0x0, 0x2), alignment=Qt.AlignRight),
            '参数二': HexSpin(None, '参数二', Value(0x0, 0x2), alignment=Qt.AlignRight),
            '扩展文本': TextLine(None, '扩展文本', Text(0x0, 0xFF, "shiftjisx0213")),
            '释义': TextLine(None, '释义', Text(0x0, 0xFF, "gb18030")),
        }, sortable=False, stretch=(3, ),)

        self['指令列表'].setObjectName("OrderList")
        self['指令列表'].horizontalHeader().setDefaultSectionSize(40)

        main_layout = QVBoxLayout()
        main_layout.addLayout(script)
        main_layout.addWidget(self['指令列表'])
        self.setLayout(main_layout)

    def init_script_table(self):
        # noinspection PyTypeChecker
        self['脚本列表'] = ScriptCombo(self)
        self['脚本列表'].setFixedWidth(1420)

        layout = QHBoxLayout()
        layout.addWidget(self['脚本列表'])
        return layout

    def control_scenario(self, index: int):
        self['剧本列表'].control_child(index)
        return True

    def set_roms(self, roms: list[ScriptBIN]):
        self.rom = roms[0]
        self.parse()

    def parse(self):
        self.rom.parse()
        self['剧本列表'].install(self.rom.data)
        self['脚本列表'].currentIndexChanged[int].connect(self.control_scenario)
        self.original_data = deepcopy(self.rom.data)
        self['指令列表'].setColumnWidth(4, 450)

    def build(self):
        self.rom.build()

    def builded(self) -> bool:
        if self.original_data == self.rom.data:
            return True
        return False
