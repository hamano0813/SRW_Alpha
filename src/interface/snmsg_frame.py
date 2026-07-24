#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import deepcopy
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLineEdit, QLabel, QVBoxLayout

from parameter import SNMSG_TEXT_EXTRA
from structure import SnmsgBIN
from structure.specific.snmsg_bin import SNMSG_STRUCTURE
from widget import *


class SnmsgFrame(BackgroundFrame):
    def __init__(self, parent=None, **kwargs):
        super(SnmsgFrame, self).__init__(parent, **kwargs)
        self.rom: Optional[SnmsgBIN] = None
        self.init_ui()

    def init_ui(self):
        snmsg_table = self.init_snmsg_table
        main_layout = QHBoxLayout()
        main_layout.addWidget(snmsg_table)
        self.setLayout(main_layout)

    @property
    def init_snmsg_table(self):
        group = FontGroup('剧情文本')
        self['文本列表'] = ArrayTable(
            self, '文本列表', {
                '文本': TextMulti(None, '文本', SNMSG_STRUCTURE['文本'],
                                extra=SNMSG_TEXT_EXTRA, ),
            }, sortable=False, alignment=Qt.AlignTop, resizeRows=False)
        self['文本列表'].setObjectName('MessageList')
        self['文本列表'].verticalHeader().setMinimumSectionSize(62)
        self['文本列表'].horizontalHeader().setHidden(True)
        layout = QHBoxLayout()
        layout.addWidget(self['文本列表'])
        filter_line = QLineEdit()
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel('文本搜索'))
        filter_layout.addWidget(filter_line)
        group_layout = QVBoxLayout()
        group_layout.addWidget(self['文本列表'])
        group_layout.addLayout(filter_layout)
        group.setLayout(group_layout)
        # noinspection PyUnresolvedReferences
        filter_line.textChanged[str].connect(self['文本列表'].filterChanged)
        return group

    def set_roms(self, roms: list[SnmsgBIN]):
        self.rom = roms[0]
        self.parse()

    def parse(self):
        self.rom.parse()
        self['文本列表'].install(self.rom.data)

        self.original_data = deepcopy(self.rom.data)

    def build(self):
        self.rom.build()

    def builded(self) -> bool:
        if self.original_data == self.rom.data:
            return True
        return False
