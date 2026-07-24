#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import deepcopy
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QVBoxLayout, QFormLayout, QGridLayout

from parameter import EnumData
from structure import PilotBIN
from structure.specific.pilot_bin import PILOT_STRUCTURE, SKILL_STRUCTURE
from widget import *


class PilotFrame(BackgroundFrame):
    def __init__(self, parent=None, **kwargs):
        super(PilotFrame, self).__init__(parent, **kwargs)
        self.rom: Optional[PilotBIN] = None
        self.lv_mapping = {lv: f'{lv}' for lv in range(1, 100)}

        self.init_ui()

    def init_ui(self):
        pilot_table = self.init_pilot_table()
        skill_table = self.init_skill_table()

        pilot_sprite = self.init_pilot_spirit()
        pilot_skill = self.init_pilot_skill()
        pilot_transfer = self.init_pilot_transfer()
        pilot_adaptation = self.init_pilot_adaptation()

        pilot_table.setFixedWidth(1070)
        skill_table.setFixedHeight(287)
        pilot_sprite.setFixedHeight(220)
        pilot_skill.setFixedSize(135, 220)
        pilot_adaptation.setFixedWidth(135)

        main_layout = QHBoxLayout()
        main_layout.addWidget(pilot_table)
        grid_layout = QGridLayout()
        grid_layout.addWidget(skill_table, 0, 0, 1, 2)
        grid_layout.addWidget(pilot_sprite, 1, 0, 1, 1)
        grid_layout.addWidget(pilot_skill, 1, 1, 1, 1)
        grid_layout.addWidget(pilot_transfer, 2, 0, 2, 1)
        grid_layout.addWidget(pilot_adaptation, 2, 1, 1, 1)
        main_layout.addLayout(grid_layout)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def init_pilot_table(self):
        group = FontGroup('机师列表')
        self['机师列表'] = ArrayTable(
            self, '机师列表', {
                '机师': TextLine(None, '机师', PILOT_STRUCTURE['机师']),
                '全名': TextLine(None, '全名', PILOT_STRUCTURE['全名']),
                '格斗': ValueSpin(None, '格斗', PILOT_STRUCTURE['格斗'], alignment=Qt.AlignRight),
                '射撃': ValueSpin(None, '射撃', PILOT_STRUCTURE['射撃'], alignment=Qt.AlignRight),
                '回避': ValueSpin(None, '回避', PILOT_STRUCTURE['回避'], alignment=Qt.AlignRight),
                '命中': ValueSpin(None, '命中', PILOT_STRUCTURE['命中'], alignment=Qt.AlignRight),
                '反应': ValueSpin(None, '反应', PILOT_STRUCTURE['反应'], alignment=Qt.AlignRight),
                '技量': ValueSpin(None, '技量', PILOT_STRUCTURE['技量'], alignment=Qt.AlignRight),
                '性格': RadioCombo(self['机师列表'], '性格', PILOT_STRUCTURE['性格'],
                                 mapping=EnumData.PILOT['性格']),
                'ＳＰ': ValueSpin(None, 'ＳＰ', PILOT_STRUCTURE['ＳＰ'], alignment=Qt.AlignRight),
                '２回行动': ValueSpin(None, '２回行动', PILOT_STRUCTURE['２回行动'], alignment=Qt.AlignRight),
                '气力组': ValueSpin(self['机师列表'], '气力组', PILOT_STRUCTURE['气力组'], alignment=Qt.AlignRight),
            },
            stretch=(1,)
        )
        filter_line = QLineEdit()
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(FontLabel('机师搜索'))
        filter_layout.addWidget(filter_line)
        group_layout = QVBoxLayout()
        group_layout.addWidget(self['机师列表'])
        group_layout.addLayout(filter_layout)
        group.setLayout(group_layout)
        # noinspection PyUnresolvedReferences
        filter_line.textChanged[str].connect(self['机师列表'].filterChanged)
        return group

    def init_skill_table(self):
        group = FontGroup('升级技能')
        self['技能'] = TransposeTable(
            self['机师列表'], '技能列表', {
                '技能': RadioCombo(None, '技能', SKILL_STRUCTURE['技能'],
                                 mapping=EnumData.PILOT['技能'], alignment=Qt.AlignLeft),
                'L1': MappingSpin(None, 'L1', SKILL_STRUCTURE['L1'],
                                  mapping=self.lv_mapping | {0xFF: '一'}, alignment=Qt.AlignRight),
                'L2': MappingSpin(None, 'L2', SKILL_STRUCTURE['L2'],
                                  mapping=self.lv_mapping | {0xFF: '一'}, alignment=Qt.AlignRight),
                'L3': MappingSpin(None, 'L3', SKILL_STRUCTURE['L3'],
                                  mapping=self.lv_mapping | {0xFF: '一'}, alignment=Qt.AlignRight),
                'L4': MappingSpin(None, 'L4', SKILL_STRUCTURE['L4'],
                                  mapping=self.lv_mapping | {0xFF: '一'}, alignment=Qt.AlignRight),
                'L5': MappingSpin(None, 'L5', SKILL_STRUCTURE['L5'],
                                  mapping=self.lv_mapping | {0xFF: '一'}, alignment=Qt.AlignRight),
                'L6': MappingSpin(None, 'L6', SKILL_STRUCTURE['L6'],
                                  mapping=self.lv_mapping | {0xFF: '一'}, alignment=Qt.AlignRight),
                'L7': MappingSpin(None, 'L7', SKILL_STRUCTURE['L7'],
                                  mapping=self.lv_mapping | {0xFF: '一'}, alignment=Qt.AlignRight),
                'L8': MappingSpin(None, 'L8', SKILL_STRUCTURE['L8'],
                                  mapping=self.lv_mapping | {0xFF: '一'}, alignment=Qt.AlignRight),
                'L9': MappingSpin(None, 'L9', SKILL_STRUCTURE['L9'],
                                  mapping=self.lv_mapping | {0xFF: '一'}, alignment=Qt.AlignRight),
            }
        )
        group_layout = QVBoxLayout()
        group_layout.addWidget(self['技能'])
        group.setLayout(group_layout)
        return group

    def init_pilot_skill(self):
        group = FontGroup('特殊技能')
        self['特殊技能'] = CheckList(self['机师列表'], '特殊技能', PILOT_STRUCTURE['特殊技能'],
                                 item_list=EnumData.PILOT['特殊技能'])
        group_layout = QVBoxLayout()
        group_layout.addWidget(self['特殊技能'])
        group.setLayout(group_layout)
        return group

    def init_pilot_transfer(self):
        group = FontGroup('换乘系')
        self['换乘系'] = CheckList(self['机师列表'], '换乘系', PILOT_STRUCTURE['换乘系'],
                                EnumData.PILOT['换乘系'])
        group_layout = QVBoxLayout()
        group_layout.addWidget(self['换乘系'])
        group.setLayout(group_layout)
        return group

    def init_pilot_adaptation(self):
        group = FontGroup('地形适应')
        self['空适应'] = MappingSpin(self['机师列表'], '空适应', PILOT_STRUCTURE['空适应'], EnumData.PILOT['適応'])
        self['陆适应'] = MappingSpin(self['机师列表'], '陆适应', PILOT_STRUCTURE['陆适应'], EnumData.PILOT['適応'])
        self['海适应'] = MappingSpin(self['机师列表'], '海适应', PILOT_STRUCTURE['海适应'], EnumData.PILOT['適応'])
        self['宇适应'] = MappingSpin(self['机师列表'], '宇适应', PILOT_STRUCTURE['宇适应'], EnumData.PILOT['適応'])
        group_layout = QFormLayout()
        group_layout.addRow(FontLabel('空适应'), self['空适应'])
        group_layout.addRow(FontLabel('陆适应'), self['陆适应'])
        group_layout.addRow(FontLabel('海适应'), self['海适应'])
        group_layout.addRow(FontLabel('宇适应'), self['宇适应'])
        group.setLayout(group_layout)
        return group

    def init_pilot_spirit(self):
        group = FontGroup('精神列表')
        self['精神列表'] = ParallelTable(
            self['机师列表'], ('精神列表', '习得列表'), {
                '精神': RadioCombo(None, '精神', PILOT_STRUCTURE['精神列表']['精神'], mapping=EnumData.SPIRIT),
                '习得': MappingSpin(None, '习得', PILOT_STRUCTURE['习得列表']['习得'],
                                  mapping=self.lv_mapping | {0xFF: '一'}, alignment=Qt.AlignRight),
            }
        )
        group_layout = QVBoxLayout()
        group_layout.addWidget(self['精神列表'])
        group.setLayout(group_layout)
        return group

    def set_roms(self, roms: list[PilotBIN]):
        self.rom = roms[0]
        self.parse()

    def parse(self):
        self.rom.parse()
        self['机师列表'].install(self.rom.data)

        self.original_data = deepcopy(self.rom.data)

    def build(self):
        self.rom.build()

    def builded(self) -> bool:
        if self.original_data == self.rom.data:
            return True
        return False
