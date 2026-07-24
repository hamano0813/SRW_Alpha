#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import deepcopy
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QTabWidget, QFrame, QVBoxLayout, QFormLayout

from parameter import EnumData
from structure import SndataBIN, EnlistBIN, AiunpBIN
from structure.specific.aiunp_bin import AI_STRUCTURE
from structure.specific.enlist_bin import ENLIST_STRUCTURE, ENEMY_STRUCTURE
from widget import *


class ScenarioFrame(BackgroundFrame):
    def __init__(self, parent=None, **kwargs):
        super(ScenarioFrame, self).__init__(parent, **kwargs)
        self.sndata_rom: Optional[SndataBIN] = None
        self.enlist_rom: Optional[EnlistBIN] = None
        self.aiunp_rom: Optional[AiunpBIN] = None

        self.scenario_tab = QTabWidget()
        self.scenario_tab.tabBar().setProperty('language', 'zhb')

        self.robot_mapping = kwargs.get('robots', dict())
        self.pilot_mapping = kwargs.get('pilots', dict()) | {0x7D0: '[7D0]主人公', 0x7D1: '[7D1]恋人', 0x7FA: '[7FA]？？？'}
        self.message_mapping = kwargs.get('messages', dict())
        self.group_mapping = {group: f'{group}' for group in range(0, 16)}
        self.lv_mapping = {lv: f'{lv}' for lv in range(1, 100)}
        self.upgrade_mapping = {upgrade: f'{upgrade}' for upgrade in range(1, 11)} | {0: '一'}
        self.pos_mapping = {p: f'{p}' for p in range(1, 40)} | {101: '北', 102: '東', 103: '南', 104: '西', 0xFF: '一'}
        self.phase_mapping = {phase: f'{phase}' for phase in range(1, 20)} | {0: '一'}

        self.init_ui()

    def init_ui(self):
        scenario = self.init_scenario_table()

        self.scenario_tab.addTab(self.init_stage_frame(), '场景设计')
        self.scenario_tab.addTab(self.init_enemy_frame(), '敌方设计')
        self.scenario_tab.addTab(self.init_ai_frame(), 'AI设计')

        main_layout = QVBoxLayout()
        main_layout.addLayout(scenario)
        main_layout.addWidget(self.scenario_tab)
        self.setLayout(main_layout)

    def init_scenario_table(self):
        # noinspection PyTypeChecker
        self['シナリオ列表'] = ScenarioCombo(self)
        self['シナリオ列表'].setFixedWidth(1420)
        layout = QHBoxLayout()
        layout.addWidget(self['シナリオ列表'])
        return layout

    def init_stage_frame(self):
        self['场景设计'] = ArrayTable(self, '场景设计', {}, stretch=tuple())
        stage_frame = StageFrame(self['场景设计'], 'Commands', corner='索引',
                                 robots=self.robot_mapping,
                                 pilots=self.pilot_mapping,
                                 messages=self.message_mapping,
                                 )
        stage_frame.jumpSearch[int, int].connect(self.jump_search)
        return stage_frame

    def init_enemy_frame(self):
        enemy_frame = QFrame()

        self['敌方设计'] = ArrayTable(self, '敌方设计', {}, stretch=tuple())

        self['合计'] = ValueSpin(self['敌方设计'], '合计', ENLIST_STRUCTURE['合计'], alignment=Qt.AlignRight)
        self['组数'] = ValueSpin(self['敌方设计'], '组数', ENLIST_STRUCTURE['组数'], alignment=Qt.AlignRight)
        quantity_layout = QFormLayout()
        quantity_layout.addRow('合计', self['合计'])
        quantity_layout.addRow('组数', self['组数'])

        self['合计'].setEnabled(False)
        self['组数'].setEnabled(False)
        for idx in range(0, 16):
            self[f'组{idx:02d}'] = ValueSpin(self['敌方设计'], f'组{idx:02d}', ENLIST_STRUCTURE[f'组{idx:02d}'],
                                            alignment=Qt.AlignRight)
            quantity_layout.addRow(f'组{idx:02d}', self[f'组{idx:02d}'])
            # noinspection PyUnresolvedReferences
            self[f'组{idx:02d}'].valueChanged.connect(self.reset_count)

        self['敌方列表'] = ArrayTable(
            self['敌方设计'], '敌方列表', {
                '机师': RadioCombo(None, '机师', ENEMY_STRUCTURE['机师'],
                                 mapping=self.pilot_mapping | {0x0: '一一'}),
                '机体': RadioCombo(None, '机体', ENEMY_STRUCTURE['机体'], mapping=self.robot_mapping | {0x0: '一一'}),
                '组号': MappingSpin(None, '组号', ENEMY_STRUCTURE['组号'],
                                  mapping=self.group_mapping, alignment=Qt.AlignRight),
                '等级': ValueSpin(None, '等级', ENEMY_STRUCTURE['等级'], alignment=Qt.AlignRight),
                '机体改造': MappingSpin(None, '机体改造', ENEMY_STRUCTURE['机体改造'],
                                    mapping=self.upgrade_mapping, alignment=Qt.AlignRight),
                '武器改造': MappingSpin(None, '武器改造', ENEMY_STRUCTURE['武器改造'],
                                    mapping=self.upgrade_mapping, alignment=Qt.AlignRight),
                '坐标X': ValueSpin(None, '坐标X', ENEMY_STRUCTURE['坐标X'], alignment=Qt.AlignRight),
                '坐标Y': ValueSpin(None, '坐标Y', ENEMY_STRUCTURE['坐标Y'], alignment=Qt.AlignRight),
                '芯片': RadioCombo(None, '芯片', ENEMY_STRUCTURE['芯片'], mapping=EnumData.PART),
            }, sortable=False, stretch=(0, 1, 8),
        )
        self['敌方列表'].horizontalHeader().setObjectName('ENLIST')

        enemy_layout = QHBoxLayout()
        enemy_layout.addWidget(self['敌方列表'])
        enemy_layout.addLayout(quantity_layout)
        enemy_frame.setLayout(enemy_layout)
        return enemy_frame

    def init_ai_frame(self):
        ai_frame = QFrame()
        self['AI设计'] = ArrayTable(self, 'AI设计', {}, stretch=tuple())
        self['AI列表'] = AiTable(self['AI设计'], 'AI列表', {
            'AI': RadioCombo(None, 'AI', AI_STRUCTURE['AI'], mapping=self.pilot_mapping | {0x0: '一一'}),
            '目标机师': RadioCombo(None, '目标机师', AI_STRUCTURE['目标机师'],
                               mapping=self.pilot_mapping | {0xFFFF: '一一'}),
            '目标X': RadioCombo(None, '目标X', AI_STRUCTURE['目标X'],
                              mapping=self.pos_mapping, alignment=Qt.AlignLeft),
            '目标Y': RadioCombo(None, '目标Y', AI_STRUCTURE['目标Y'],
                              mapping=self.pos_mapping, alignment=Qt.AlignLeft),
            '移动开始': MappingSpin(None, '移动开始', AI_STRUCTURE['移动开始'],
                                mapping=self.phase_mapping, alignment=Qt.AlignRight),
            '不明10': ValueSpin(None, '不明10', AI_STRUCTURE['不明10'], alignment=Qt.AlignRight),
            '不明12': ValueSpin(None, '不明12', AI_STRUCTURE['不明12'], alignment=Qt.AlignRight),
            '不明13': ValueSpin(None, '不明13', AI_STRUCTURE['不明13'], alignment=Qt.AlignRight),
            '不明14': ValueSpin(None, '不明14', AI_STRUCTURE['不明14'], alignment=Qt.AlignRight),
            '不明15': ValueSpin(None, '不明15', AI_STRUCTURE['不明15'], alignment=Qt.AlignRight),
            '不明16': ValueSpin(None, '不明16', AI_STRUCTURE['不明16'], alignment=Qt.AlignRight),
            '不明17': ValueSpin(None, '不明17', AI_STRUCTURE['不明17'], alignment=Qt.AlignRight),
            '不明30': ValueSpin(None, '不明30', AI_STRUCTURE['不明30'], alignment=Qt.AlignRight),
            '不明31': ValueSpin(None, '不明31', AI_STRUCTURE['不明31'], alignment=Qt.AlignRight),
            '不明32': ValueSpin(None, '不明32', AI_STRUCTURE['不明32'], alignment=Qt.AlignRight),
            '不明34': ValueSpin(None, '不明34', AI_STRUCTURE['不明34'], alignment=Qt.AlignRight),
            '不明44': ValueSpin(None, '不明44', AI_STRUCTURE['不明44'], alignment=Qt.AlignRight),
            '自主移动': ValueSpin(None, '自主移动', AI_STRUCTURE['自主移动'], alignment=Qt.AlignRight),
            '不明46': ValueSpin(None, '不明46', AI_STRUCTURE['不明46'], alignment=Qt.AlignRight),
            '自主攻击': ValueSpin(None, '自主攻击', AI_STRUCTURE['自主攻击'], alignment=Qt.AlignRight),
            '生效': ValueSpin(None, '生效', AI_STRUCTURE['生效'], alignment=Qt.AlignRight),
        }, check=tuple(range(5, 21)), sortable=False, stretch=(0, 1), )

        self['AI列表'].horizontalHeader().setObjectName('ENLIST')
        self['AI列表'].horizontalHeader().setMinimumSectionSize(56)

        ai_layout = QHBoxLayout()
        ai_layout.addWidget(self['AI列表'])
        ai_frame.setLayout(ai_layout)
        return ai_frame

    def reset_count(self):
        amout = count = 0
        for idx in range(0, 16):
            if (value := self[f'组{idx:02d}'].value()) > 0:
                amout += value
                count += 1
        self['合计'].setValue(amout)
        self['组数'].setValue(count)

    def control_scenario(self, index: int):
        self['场景设计'].control_child(index)
        self['敌方设计'].control_child(index)
        self['AI设计'].control_child(index)
        return True

    def jump_search(self, scenario: int, pos: int):
        self['シナリオ列表'].setCurrentIndex(list(EnumData.SCENARIO.keys()).index(scenario))
        self.scenario_tab.widget(0).table.jump_pos(pos)

    def set_roms(self, roms: list[SndataBIN, EnlistBIN, AiunpBIN]):
        self.sndata_rom, self.enlist_rom, self.aiunp_rom = roms
        self.parse()

    def parse(self):
        self.sndata_rom.parse()
        self.enlist_rom.parse()
        self.aiunp_rom.parse()
        self['场景设计'].install(self.sndata_rom.data)
        self['敌方设计'].install(self.enlist_rom.data)
        self['AI设计'].install(self.aiunp_rom.data)

        # noinspection PyUnresolvedReferences
        self['シナリオ列表'].currentIndexChanged[int].connect(self.control_scenario)

        self.original_data = dict()
        self.original_data['场景设计'] = deepcopy(self.sndata_rom.data)
        self.original_data['敌方设计'] = deepcopy(self.enlist_rom.data)
        self.original_data['AI设计'] = deepcopy(self.aiunp_rom.data)

    def build(self):
        self.sndata_rom.build()
        self.enlist_rom.build()
        self.aiunp_rom.build()

    def builded(self) -> bool:
        scenario = self.original_data['场景设计'] == self.sndata_rom.data
        enemy = self.original_data['敌方设计'] == self.enlist_rom.data
        ai = self.original_data['AI设计'] == self.aiunp_rom.data
        if all((scenario, enemy, ai)):
            return True
        return False
