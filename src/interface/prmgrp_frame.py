#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import deepcopy
from typing import Optional

from PySide6.QtCore import Qt, QModelIndex
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QTabWidget, QFrame

from parameter import EnumData
from structure import PrmgrpBIN
from structure.specific.prmgrp_bin import (SPECIAL_STRUCTURE, ZODIAC_STRUCTURE, BLOOD_STRUCTURE, PART_STRUCTURE,
                                           UPGRADE_STRUCTURE)
from widget import *


class PrmgrpFrame(BackgroundFrame):
    def __init__(self, parent=None, **kwargs):
        super(PrmgrpFrame, self).__init__(parent, **kwargs)
        self.rom: Optional[PrmgrpBIN] = None
        self.skill_mapping = {idx: f' {idx:02d}.{skill}' for idx, skill in enumerate(EnumData.PILOT['特殊技能'][:8])}
        self.spirit_sequence = [{'精神': spirit} for spirit in EnumData.SPIRIT.values()][:-1]
        self.part_sequence = [{'芯片': part} for part in EnumData.PART.values()][1:]
        self.lv_mapping = {lv: f'{lv}' for lv in range(1, 100)}
        self.month_mapping = {month: f'{month}' for month in range(1, 13)}
        self.day_mapping = {day: f'{day}' for day in range(1, 32)}

        self.init_ui()

    def init_ui(self):
        tab_widget = QTabWidget()
        tab_widget.tabBar().setProperty('language', 'zhb')

        tab_widget.addTab(self.init_upgrade_frame(), '改造')
        tab_widget.addTab(self.init_birthday_frame(), '生日')
        tab_widget.addTab(self.init_sppart_frame(), '精神消费＆芯片属性')

        main_layout = QHBoxLayout()
        main_layout.addWidget(tab_widget)
        self.setLayout(main_layout)

    def init_upgrade_frame(self):
        frame = QFrame()

        robot_group = FontGroup('机体改造')

        self['ＨＰ改造'] = ArrayTable(
            self, 'ＨＰ改造', {
                '费用': ValueSpin(None, '费用', UPGRADE_STRUCTURE['ＨＰ改造']['费用'], alignment=Qt.AlignRight),
                '上升值': ValueSpin(None, '上升值', UPGRADE_STRUCTURE['ＨＰ改造']['上升值'], alignment=Qt.AlignRight),
            }, sortable=False, stretch=tuple(), corner='   ＨＰ',
        )
        self['ＨＰ改造'].verticalHeader().setFixedWidth(60)
        self['ＨＰ改造'].setFixedSize(206, 293)

        self['ＥＮ改造'] = ArrayTable(
            self, 'ＥＮ改造', {
                '费用': ValueSpin(None, '费用', UPGRADE_STRUCTURE['ＥＮ改造']['费用'], alignment=Qt.AlignRight),
                '上升值': ValueSpin(None, '上升值', UPGRADE_STRUCTURE['ＥＮ改造']['上升值'], alignment=Qt.AlignRight),
            }, sortable=False, stretch=tuple(), corner='   ＥＮ',
        )
        self['ＥＮ改造'].verticalHeader().setFixedWidth(60)
        self['ＥＮ改造'].setFixedSize(206, 293)

        self['运动改造'] = ArrayTable(
            self, '运动改造', {
                '费用': ValueSpin(None, '费用', UPGRADE_STRUCTURE['运动改造']['费用'], alignment=Qt.AlignRight),
                '上升值': ValueSpin(None, '上升值', UPGRADE_STRUCTURE['运动改造']['上升值'], alignment=Qt.AlignRight),
            }, sortable=False, stretch=tuple(), corner='   運動',
        )
        self['运动改造'].verticalHeader().setFixedWidth(60)
        self['运动改造'].setFixedSize(206, 293)

        self['装甲改造'] = ArrayTable(
            self, '装甲改造', {
                '费用': ValueSpin(None, '费用', UPGRADE_STRUCTURE['装甲改造']['费用'], alignment=Qt.AlignRight),
                '上升值': ValueSpin(None, '上升值', UPGRADE_STRUCTURE['装甲改造']['上升值'], alignment=Qt.AlignRight),
            }, sortable=False, stretch=tuple(), corner='   装甲',
        )
        self['装甲改造'].verticalHeader().setFixedWidth(60)
        self['装甲改造'].setFixedSize(206, 293)

        self['限界改造'] = ArrayTable(
            self, '限界改造', {
                '费用': ValueSpin(None, '费用', UPGRADE_STRUCTURE['限界改造']['费用'], alignment=Qt.AlignRight),
                '上升值': ValueSpin(None, '上升值', UPGRADE_STRUCTURE['限界改造']['上升值'], alignment=Qt.AlignRight),
            }, sortable=False, stretch=tuple(), corner='   限界',
        )
        self['限界改造'].verticalHeader().setFixedWidth(60)
        self['限界改造'].setFixedSize(206, 293)

        robot_layout = QHBoxLayout()
        robot_layout.addWidget(self['ＨＰ改造'])
        robot_layout.addWidget(self['ＥＮ改造'])
        robot_layout.addWidget(self['运动改造'])
        robot_layout.addWidget(self['装甲改造'])
        robot_layout.addWidget(self['限界改造'])
        robot_group.setLayout(robot_layout)

        weapon_group = FontGroup('武器改造')

        self['类型[A]'] = ArrayTable(
            self, '类型[A]', {
                '费用': ValueSpin(None, '费用', UPGRADE_STRUCTURE['类型[A]']['费用'],
                                multiple=10, alignment=Qt.AlignRight),
                '上升值': ValueSpin(None, '上升值', UPGRADE_STRUCTURE['类型[A]']['上升值'], alignment=Qt.AlignRight),
            }, sortable=False, stretch=tuple(), corner='类型[A]',
        )
        self['类型[A]'].verticalHeader().setFixedWidth(60)
        self['类型[A]'].setFixedSize(206, 293)

        self['类型[B]'] = ArrayTable(
            self, '类型[B]', {
                '费用': ValueSpin(None, '费用', UPGRADE_STRUCTURE['类型[B]']['费用'],
                                multiple=10, alignment=Qt.AlignRight),
                '上升值': ValueSpin(None, '上升值', UPGRADE_STRUCTURE['类型[B]']['上升值'], alignment=Qt.AlignRight),
            }, sortable=False, stretch=tuple(), corner='类型[B]',
        )
        self['类型[B]'].verticalHeader().setFixedWidth(60)
        self['类型[B]'].setFixedSize(206, 293)

        self['类型[C]'] = ArrayTable(
            self, '类型[C]', {
                '费用': ValueSpin(None, '费用', UPGRADE_STRUCTURE['类型[C]']['费用'],
                                multiple=10, alignment=Qt.AlignRight),
                '上升值': ValueSpin(None, '上升值', UPGRADE_STRUCTURE['类型[C]']['上升值'], alignment=Qt.AlignRight),
            }, sortable=False, stretch=tuple(), corner='类型[C]',
        )
        self['类型[C]'].verticalHeader().setFixedWidth(60)
        self['类型[C]'].setFixedSize(206, 293)

        self['类型[D]'] = ArrayTable(
            self, '类型[D]', {
                '费用': ValueSpin(None, '费用', UPGRADE_STRUCTURE['类型[D]']['费用'],
                                multiple=10, alignment=Qt.AlignRight),
                '上升值': ValueSpin(None, '上升值', UPGRADE_STRUCTURE['类型[D]']['上升值'], alignment=Qt.AlignRight),
            }, sortable=False, stretch=tuple(), corner='类型[D]',
        )
        self['类型[D]'].verticalHeader().setFixedWidth(60)
        self['类型[D]'].setFixedSize(206, 293)

        weapon_layout = QHBoxLayout()
        weapon_layout.addWidget(self['类型[A]'])
        weapon_layout.addWidget(self['类型[B]'])
        weapon_layout.addWidget(self['类型[C]'])
        weapon_layout.addWidget(self['类型[D]'])
        weapon_group.setLayout(weapon_layout)

        frame_layout = QVBoxLayout()
        frame_layout.addWidget(robot_group, alignment=Qt.AlignLeft)
        frame_layout.addWidget(weapon_group, alignment=Qt.AlignLeft)
        frame_layout.addStretch()
        frame.setLayout(frame_layout)
        return frame

    def init_birthday_frame(self):
        frame = QFrame()

        special_group = FontGroup('特殊生日')
        self['特殊生日'] = ArrayTable(
            self, '特殊生日', {
                '诞生月': MappingSpin(None, '诞生月', SPECIAL_STRUCTURE['诞生月'],
                                   mapping=self.month_mapping, alignment=Qt.AlignRight),
                '诞生日': MappingSpin(None, '诞生日', SPECIAL_STRUCTURE['诞生日'],
                                   mapping=self.day_mapping, alignment=Qt.AlignRight),
                '血型': MappingSpin(None, '血型', SPECIAL_STRUCTURE['血型'],
                                  mapping={0: 'A', 1: 'B', 2: 'AB', 3: 'O'}, alignment=Qt.AlignRight),
            }, sortable=False, stretch=tuple(), single=True,
        )
        self['特殊精神'] = ParallelTable(
            self['特殊生日'], ('精神列表', '习得列表'), {
                '精神': RadioCombo(None, '精神', SPECIAL_STRUCTURE['精神列表']['精神'], mapping=EnumData.SPIRIT),
                '习得': MappingSpin(None, '习得', SPECIAL_STRUCTURE['习得列表']['习得'],
                                  mapping=self.lv_mapping, alignment=Qt.AlignRight),
            }
        )
        self['特殊特殊技能'] = RadioCombo(self['特殊生日'], '特殊技能', SPECIAL_STRUCTURE['特殊技能'],
                                    mapping=self.skill_mapping,
                                    alignment=Qt.AlignRight)

        self['特殊生日'].setFixedWidth(231)
        self['特殊生日'].verticalHeader().setHidden(True)
        self['特殊精神'].setFixedSize(148, 189)

        special_layout = QHBoxLayout()

        spirit_layout = QVBoxLayout()
        spirit_layout.addWidget(self['特殊精神'])
        spirit_layout.addWidget(self['特殊特殊技能'])
        spirit_layout.addStretch()
        special_layout.addWidget(self['特殊生日'])
        special_layout.addLayout(spirit_layout)
        special_group.setLayout(special_layout)

        constellation_group = FontGroup('星座生日')
        self['星座范围'] = ArrayTable(
            self, '星座范围', {
                '开始月': MappingSpin(None, '开始月', ZODIAC_STRUCTURE['开始月'],
                                   mapping=self.month_mapping, alignment=Qt.AlignRight),
                '开始日': MappingSpin(None, '开始日', ZODIAC_STRUCTURE['开始日'],
                                   mapping=self.day_mapping, alignment=Qt.AlignRight),
                '结束月': MappingSpin(None, '结束月', ZODIAC_STRUCTURE['结束月'],
                                   mapping=self.month_mapping, alignment=Qt.AlignRight),
                '结束日': MappingSpin(None, '结束日', ZODIAC_STRUCTURE['结束日'],
                                   mapping=self.day_mapping, alignment=Qt.AlignRight),
            },
            sortable=False, stretch=tuple(), single=True,
        )
        self['血型A'] = ArrayTable(self, '血型A', {}, stretch=tuple())
        self['血型B'] = ArrayTable(self, '血型B', {}, stretch=tuple())
        self['血型AB'] = ArrayTable(self, '血型AB', {}, stretch=tuple())
        self['血型O'] = ArrayTable(self, '血型O', {}, stretch=tuple())

        self['血型A精神'] = ParallelTable(
            self['血型A'], ('精神列表', '习得列表'), {
                '精神': RadioCombo(None, '精神', BLOOD_STRUCTURE['精神列表']['精神'], mapping=EnumData.SPIRIT),
                '习得': MappingSpin(None, '习得', BLOOD_STRUCTURE['习得列表']['习得'],
                                  mapping=self.lv_mapping, alignment=Qt.AlignRight),
            }
        )
        self['血型B精神'] = ParallelTable(
            self['血型B'], ('精神列表', '习得列表'), {
                '精神': RadioCombo(None, '精神', BLOOD_STRUCTURE['精神列表']['精神'], mapping=EnumData.SPIRIT),
                '习得': MappingSpin(None, '习得', BLOOD_STRUCTURE['习得列表']['习得'],
                                  mapping=self.lv_mapping, alignment=Qt.AlignRight),
            }
        )
        self['血型AB精神'] = ParallelTable(
            self['血型AB'], ('精神列表', '习得列表'), {
                '精神': RadioCombo(None, '精神', BLOOD_STRUCTURE['精神列表']['精神'], mapping=EnumData.SPIRIT),
                '习得': MappingSpin(None, '习得', BLOOD_STRUCTURE['习得列表']['习得'],
                                  mapping=self.lv_mapping, alignment=Qt.AlignRight),
            }
        )
        self['血型O精神'] = ParallelTable(
            self['血型O'], ('精神列表', '习得列表'), {
                '精神': RadioCombo(None, '精神', BLOOD_STRUCTURE['精神列表']['精神'], mapping=EnumData.SPIRIT),
                '习得': MappingSpin(None, '习得', BLOOD_STRUCTURE['习得列表']['习得'],
                                  mapping=self.lv_mapping, alignment=Qt.AlignRight),
            }
        )
        self['血型A特殊技能'] = RadioCombo(self['血型A'], '特殊技能', BLOOD_STRUCTURE['特殊技能'],
                                     mapping=self.skill_mapping, alignment=Qt.AlignRight)
        self['血型B特殊技能'] = RadioCombo(self['血型B'], '特殊技能', BLOOD_STRUCTURE['特殊技能'],
                                     mapping=self.skill_mapping, alignment=Qt.AlignRight)
        self['血型AB特殊技能'] = RadioCombo(self['血型AB'], '特殊技能', BLOOD_STRUCTURE['特殊技能'],
                                      mapping=self.skill_mapping, alignment=Qt.AlignRight)
        self['血型O特殊技能'] = RadioCombo(self['血型O'], '特殊技能', BLOOD_STRUCTURE['特殊技能'],
                                     mapping=self.skill_mapping, alignment=Qt.AlignRight)
        # noinspection PyUnresolvedReferences
        self['星座范围'].clicked[QModelIndex].connect(self.control_blood)

        self['星座范围'].verticalHeader().setHidden(True)
        self['星座范围'].setFixedSize(286, 345)
        self['血型A精神'].setFixedSize(148, 189)
        self['血型B精神'].setFixedSize(148, 189)
        self['血型AB精神'].setFixedSize(148, 189)
        self['血型O精神'].setFixedSize(148, 189)
        constellation_layout = QHBoxLayout()

        birth_layout = QVBoxLayout()
        birth_layout.addWidget(FontLabel('星座范围'))
        birth_layout.addWidget(self['星座范围'])
        birth_layout.addStretch()

        a_layout = QVBoxLayout()
        a_layout.addWidget(FontLabel('血型A'))
        a_layout.addWidget(self['血型A精神'])
        a_layout.addWidget(self['血型A特殊技能'])

        b_layout = QVBoxLayout()
        b_layout.addWidget(FontLabel('血型B'))
        b_layout.addWidget(self['血型B精神'])
        b_layout.addWidget(self['血型B特殊技能'])

        a_layout.addWidget(FontLabel('血型AB'))
        a_layout.addWidget(self['血型AB精神'])
        a_layout.addWidget(self['血型AB特殊技能'])
        a_layout.addStretch()

        b_layout.addWidget(FontLabel('血型O'))
        b_layout.addWidget(self['血型O精神'])
        b_layout.addWidget(self['血型O特殊技能'])
        b_layout.addStretch()

        constellation_layout.addLayout(birth_layout)
        constellation_layout.addLayout(a_layout)
        constellation_layout.addLayout(b_layout)

        constellation_group.setLayout(constellation_layout)

        frame_layout = QHBoxLayout()
        frame_layout.addWidget(special_group)
        frame_layout.addWidget(constellation_group)
        frame_layout.addStretch()
        frame.setLayout(frame_layout)
        return frame

    def init_sppart_frame(self):
        frame = QFrame()

        sp_group = FontGroup('精神消费')
        self['精神消费'] = ArrayTable(
            self, '精神消费', {
                '精神': TextLine(None, '精神', PrmgrpBIN().structures['精神名称'].structures['名称']),
                'SP': ValueSpin(None, 'SP', PrmgrpBIN().structures['精神消费']['SP'], alignment=Qt.AlignRight),
            }, sortable=False,
        )
        sp_layout = QHBoxLayout()
        sp_layout.addWidget(self['精神消费'])
        sp_group.setLayout(sp_layout)

        part_group = FontGroup('芯片属性')
        self['芯片属性'] = ArrayTable(
            self, '芯片属性', {
                '芯片': TextLine(None, '芯片', PrmgrpBIN().structures['芯片名称'].structures['名称']),
                'ＨＰ': ValueSpin(None, 'ＨＰ', PART_STRUCTURE['ＨＰ'], multiple=100, alignment=Qt.AlignRight),
                '装甲': ValueSpin(None, '装甲', PART_STRUCTURE['装甲'], multiple=50, alignment=Qt.AlignRight),
                '运动性': ValueSpin(None, '运动性', PART_STRUCTURE['运动性'], alignment=Qt.AlignRight),
                '限界': ValueSpin(None, '限界', PART_STRUCTURE['限界'], alignment=Qt.AlignRight),
                '移动力': ValueSpin(None, '移动力', PART_STRUCTURE['移动力'], alignment=Qt.AlignRight),
                '射程命中': RadioCombo(None, '射程命中', PART_STRUCTURE['射程命中'],
                                   mapping={0: '', 0b1: '射程+1', 0b11: '命中+30%'}, alignment=Qt.AlignLeft),
                '空A': ValueSpin(None, '空A', PART_STRUCTURE['空A'], alignment=Qt.AlignLeft),
            }, sortable=False, stretch=(6,), check=(7,)
        )
        part_layout = QHBoxLayout()
        part_layout.addWidget(self['芯片属性'])
        part_group.setLayout(part_layout)

        sp_group.setFixedWidth(226)
        part_group.setFixedWidth(710)

        frame_layout = QHBoxLayout()
        frame_layout.addWidget(sp_group)
        frame_layout.addWidget(part_group)
        frame_layout.addStretch()
        frame.setLayout(frame_layout)
        return frame

    def control_blood(self, index: QModelIndex):
        if not index.isValid():
            return False
        row = self['星座范围'].model().mapToSource(index).row()
        self['血型A'].control_child(row)
        self['血型B'].control_child(row)
        self['血型AB'].control_child(row)
        self['血型O'].control_child(row)
        return True

    def set_roms(self, roms: list[PrmgrpBIN]):
        self.rom = roms[0]
        self.parse()

    def parse(self):
        self.rom.parse()

        self['ＨＰ改造'].install(self.rom['改造设定'][0])
        self['ＥＮ改造'].install(self.rom['改造设定'][0])
        self['运动改造'].install(self.rom['改造设定'][0])
        self['装甲改造'].install(self.rom['改造设定'][0])
        self['限界改造'].install(self.rom['改造设定'][0])
        self['类型[A]'].install(self.rom['改造设定'][0])
        self['类型[B]'].install(self.rom['改造设定'][0])
        self['类型[C]'].install(self.rom['改造设定'][0])
        self['类型[D]'].install(self.rom['改造设定'][0])

        for idx, spirit in enumerate(self.spirit_sequence):
            self.rom['精神消费'][idx] |= spirit
        self['精神消费'].install(self.rom.data)
        for idx, part in enumerate(self.part_sequence):
            self.rom['芯片属性'][idx] |= part
        self['芯片属性'].install(self.rom.data)

        self['特殊生日'].install(self.rom.data)
        self['星座范围'].install(self.rom.data)
        self['血型A'].install(self.rom.data)
        self['血型B'].install(self.rom.data)
        self['血型AB'].install(self.rom.data)
        self['血型O'].install(self.rom.data)
        # noinspection PyUnresolvedReferences
        self['星座范围'].selectionModel().currentChanged[QModelIndex, QModelIndex].connect(self.control_blood)

        self.original_data = deepcopy(self.rom.data)

    def build(self):
        self.rom.build()

    def builded(self) -> bool:
        if self.original_data == self.rom.data:
            return True
        return False
