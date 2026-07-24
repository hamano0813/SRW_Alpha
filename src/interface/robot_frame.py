#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import deepcopy
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLineEdit, QHBoxLayout, QVBoxLayout, QFormLayout, QGridLayout, QSizePolicy, QSpacerItem

from parameter import EnumData
from structure import RobotRAF
from structure.specific.robot_raf import ROBOT_STRUCTURE, WEAPON_STRUCTURE
from widget import *


class RobotFrame(BackgroundFrame):
    def __init__(self, parent=None, **kwargs):
        super(RobotFrame, self).__init__(parent, **kwargs)
        self.rom: Optional[RobotRAF] = None
        self.init_ui()
        self.robots = kwargs.get('robots', dict())

    def init_ui(self):
        robot_table = self.init_robot_table()
        robot_data = self.init_robot_data()
        robot_special = self.init_robot_special()
        robot_transfer = self.init_robot_transfer()
        robot_skill = self.init_robot_skill()
        robot_bgm = self.init_robot_bgm()

        weapon_table = self.init_weapon_table()
        weapon_data = self.init_weapon_data()
        weapon_map = self.init_weapon_map()
        weapon_adaptation = self.init_weapon_adaptation()

        robot_table.setFixedWidth(630)
        robot_data.setFixedWidth(135)
        weapon_adaptation.setFixedWidth(135)

        top_left_layout = QHBoxLayout()
        top_left_layout.addWidget(robot_data)
        top_left_layout.addWidget(robot_special)

        top_right_layout = QGridLayout()
        top_right_layout.addWidget(robot_transfer, 0, 0, 1, 1)
        top_right_layout.addWidget(robot_skill, 0, 1, 1, 1)
        top_right_layout.addWidget(robot_bgm, 1, 0, 1, 2)

        bottom_right_layout = QGridLayout()
        bottom_right_layout.addWidget(weapon_data, 0, 0, 1, 2)
        bottom_right_layout.addWidget(weapon_map, 1, 0, 2, 1)
        bottom_right_layout.addWidget(weapon_adaptation, 1, 1, 1, 1)

        main_layout = QHBoxLayout()
        grid_layout = QGridLayout()
        grid_layout.addLayout(top_left_layout, 0, 0, 1, 1)
        grid_layout.addLayout(top_right_layout, 0, 1, 1, 1)
        grid_layout.addWidget(weapon_table, 1, 0, 1, 1)
        grid_layout.addLayout(bottom_right_layout, 1, 1, 1, 1)
        main_layout.addWidget(robot_table)
        main_layout.addLayout(grid_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def init_robot_table(self):
        group = FontGroup('机体列表')
        self['机体列表'] = ArrayTable(
            self, '机体列表', {
                '机体': TextLine(None, '机体', ROBOT_STRUCTURE['机体']),
                'ＨＰ': ValueSpin(None, 'ＨＰ', ROBOT_STRUCTURE['ＨＰ'], alignment=Qt.AlignRight),
                'ＥＮ': ValueSpin(None, 'ＥＮ', ROBOT_STRUCTURE['ＥＮ'], alignment=Qt.AlignRight),
                '运动性': ValueSpin(None, '运动性', ROBOT_STRUCTURE['运动性'], alignment=Qt.AlignRight),
                '装甲': ValueSpin(None, '装甲', ROBOT_STRUCTURE['装甲'], alignment=Qt.AlignRight),
                '限界': ValueSpin(None, '限界', ROBOT_STRUCTURE['限界'], alignment=Qt.AlignRight),
            },
        )
        filter_line = QLineEdit()
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(FontLabel('机体搜索'))
        filter_layout.addWidget(filter_line)
        group_layout = QVBoxLayout()
        group_layout.addWidget(self['机体列表'])
        group_layout.addLayout(filter_layout)
        group.setLayout(group_layout)
        # noinspection PyUnresolvedReferences
        filter_line.textChanged[str].connect(self['机体列表'].filterChanged)
        return group

    def init_robot_data(self):
        group = FontGroup('机体基础属性')
        self['移动类型'] = CheckCombo(self['机体列表'], '移动类型', ROBOT_STRUCTURE['移动类型'],
                                  EnumData.ROBOT['移动类型'])
        self['移动力'] = ValueSpin(self['机体列表'], '移动力', ROBOT_STRUCTURE['移动力'])
        self['空适应'] = MappingSpin(self['机体列表'], '空适应', ROBOT_STRUCTURE['空适应'],
                                  EnumData.ROBOT['適応'])
        self['陆适应'] = MappingSpin(self['机体列表'], '陆适应', ROBOT_STRUCTURE['陆适应'],
                                  EnumData.ROBOT['適応'])
        self['海适应'] = MappingSpin(self['机体列表'], '海适应', ROBOT_STRUCTURE['海适应'],
                                  EnumData.ROBOT['適応'])
        self['宇适应'] = MappingSpin(self['机体列表'], '宇适应', ROBOT_STRUCTURE['宇适应'],
                                  EnumData.ROBOT['適応'])
        self['体积'] = MappingSpin(self['机体列表'], '体积', ROBOT_STRUCTURE['体积'],
                                 EnumData.ROBOT['体积'])
        self['芯片'] = ValueSpin(self['机体列表'], '芯片', ROBOT_STRUCTURE['芯片'])
        form_layout = QFormLayout()
        form_layout.addRow(FontLabel('移动力'), self['移动力'])
        form_layout.addRow(FontLabel('体积'), self['体积'])
        form_layout.addRow(FontLabel('芯片'), self['芯片'])
        form_layout.addRow(FontLabel('空适应'), self['空适应'])
        form_layout.addRow(FontLabel('陆适应'), self['陆适应'])
        form_layout.addRow(FontLabel('海适应'), self['海适应'])
        form_layout.addRow(FontLabel('宇适应'), self['宇适应'])

        group_layout = QVBoxLayout()
        group_layout.addWidget(FontLabel('移动类型'))
        group_layout.addWidget(self['移动类型'])
        group_layout.addLayout(form_layout)
        group_layout.addStretch()
        group.setLayout(group_layout)
        return group

    def init_robot_special(self):
        group = FontGroup('机体特殊属性')
        self['变形组号'] = ValueSpin(self['机体列表'], '变形组号', ROBOT_STRUCTURE['变形组号'], )
        self['变形序号'] = ValueSpin(self['机体列表'], '变形序号', ROBOT_STRUCTURE['变形序号'])
        self['合体组号'] = ValueSpin(self['机体列表'], '合体组号', ROBOT_STRUCTURE['合体组号'])
        self['合体序号'] = ValueSpin(self['机体列表'], '合体序号', ROBOT_STRUCTURE['合体序号'])
        self['合体数'] = ValueSpin(self['机体列表'], '合体数', ROBOT_STRUCTURE['合体数'])
        self['分离机体'] = RadioCombo(self['机体列表'], '分离机体', ROBOT_STRUCTURE['分离机体'],
                                  mapping=self.kwargs.get('robots', dict()) | {0xFFFF: '一一'})
        self['换装系统'] = RadioCombo(self['机体列表'], '换装系统', ROBOT_STRUCTURE['换装系统'],
                                  mapping=EnumData.ROBOT['换装系统'])
        self['修理费'] = ValueSpin(self['机体列表'], '修理费', ROBOT_STRUCTURE['修理费'])
        self['资金'] = ValueSpin(self['机体列表'], '资金', ROBOT_STRUCTURE['资金'])
        group_layout = QGridLayout()
        group_layout.addWidget(FontLabel('变形组序'), 0, 0, 1, 1)
        group_layout.addWidget(self['变形组号'], 0, 1, 1, 1)
        group_layout.addWidget(self['变形序号'], 0, 2, 1, 1)
        group_layout.addWidget(FontLabel('合体组序'), 1, 0, 1, 1)
        group_layout.addWidget(self['合体组号'], 1, 1, 1, 1)
        group_layout.addWidget(self['合体序号'], 1, 2, 1, 1)
        group_layout.addWidget(FontLabel('合体数'), 2, 0, 1, 1)
        group_layout.addWidget(self['合体数'], 2, 1, 1, 1)
        group_layout.addWidget(FontLabel('分离机体'), 3, 0, 1, 4)
        group_layout.addWidget(self['分离机体'], 4, 0, 1, 4)
        group_layout.addWidget(FontLabel('换装系统'), 5, 0, 1, 4)
        group_layout.addWidget(self['换装系统'], 6, 0, 1, 4)
        group_layout.addWidget(FontLabel('资金'), 7, 0, 1, 1)
        group_layout.addWidget(self['资金'], 7, 1, 1, 3)
        group_layout.addWidget(FontLabel('修理费'), 8, 0, 1, 1)
        group_layout.addWidget(self['修理费'], 8, 1, 1, 3)
        group_layout.addItem(QSpacerItem(1, 1, QSizePolicy.Fixed, QSizePolicy.Expanding), 9, 0, 1, 1)
        group.setLayout(group_layout)
        return group

    def init_robot_transfer(self):
        group = FontGroup('换乘系')
        self['换乘系'] = CheckList(self['机体列表'], '换乘系', ROBOT_STRUCTURE['换乘系'],
                                EnumData.ROBOT['换乘系'])
        group_layout = QVBoxLayout()
        group_layout.addWidget(self['换乘系'])
        group.setLayout(group_layout)
        return group

    def init_robot_skill(self):
        group = FontGroup('机体特性')
        self['特性'] = CheckList(self['机体列表'], '特性', ROBOT_STRUCTURE['特性'],
                               item_list=EnumData.ROBOT['特性'])
        group_layout = QHBoxLayout()
        group_layout.addWidget(self['特性'])
        group.setLayout(group_layout)
        return group

    def init_robot_bgm(self):
        group = FontGroup('机体音乐')
        self['机体BGM'] = RadioCombo(self['机体列表'], '机体BGM', ROBOT_STRUCTURE['机体BGM'],
                                   mapping={k: f'[{k:02X}] {v}' for k, v in EnumData.MUSIC.items()})
        self['机体BGM'].setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        group_layout = QGridLayout()
        group_layout.addWidget(FontLabel('ＢＧＭ  '), 0, 0, 1, 1)
        group_layout.addWidget(self['机体BGM'], 0, 1, 1, 6)

        group.setLayout(group_layout)
        return group

    def init_weapon_table(self):
        group = FontGroup('武器列表')
        self['武器列表'] = ArrayTable(
            self['机体列表'], '武器列表', {
                '武器': TextLine(None, '武器', WEAPON_STRUCTURE['武器']),
                '分类': MappingSpin(None, '分类', WEAPON_STRUCTURE['分类'], EnumData.WEAPON['分类'], alignment=Qt.AlignRight),
                '攻击力': ValueSpin(None, '攻击力', WEAPON_STRUCTURE['攻击力'], alignment=Qt.AlignRight),
            },
        )
        group_layout = QVBoxLayout()
        group_layout.addWidget(self['武器列表'])
        group.setLayout(group_layout)
        group.setFixedSize(390, 480)
        return group

    def init_weapon_data(self):
        group = FontGroup('武器基础属性')
        self['属性'] = CheckCombo(self['武器列表'], '属性', WEAPON_STRUCTURE['属性'],
                                item_list=EnumData.WEAPON['属性'], dummy='')
        self['近射程'] = ValueSpin(self['武器列表'], '近射程', WEAPON_STRUCTURE['近射程'])
        self['远射程'] = ValueSpin(self['武器列表'], '远射程', WEAPON_STRUCTURE['远射程'])
        self['命中'] = ValueSpin(self['武器列表'], '命中', WEAPON_STRUCTURE['命中'])
        self['ＣＴ'] = ValueSpin(self['武器列表'], 'ＣＴ', WEAPON_STRUCTURE['ＣＴ'])
        self['新人类'] = ValueSpin(self['武器列表'], '新人类', WEAPON_STRUCTURE['新人类'])
        self['圣战士'] = ValueSpin(self['武器列表'], '圣战士', WEAPON_STRUCTURE['圣战士'])
        self['气力'] = ValueSpin(self['武器列表'], '气力', WEAPON_STRUCTURE['气力'])
        self['改造类型'] = MappingSpin(self['武器列表'], '改造类型', WEAPON_STRUCTURE['改造类型'],
                                   mapping=EnumData.WEAPON['改造类型'])
        self['改造追加'] = MappingSpin(self['武器列表'], '改造追加', WEAPON_STRUCTURE['改造追加'],
                                   mapping={i: f'[{i:X}]' for i in range(0x10)})
        self['初期弹数'] = ValueSpin(self['武器列表'], '初期弹数', WEAPON_STRUCTURE['初期弹数'])
        self['最大弹数'] = ValueSpin(self['武器列表'], '最大弹数', WEAPON_STRUCTURE['最大弹数'])
        self['ＥＮ'] = ValueSpin(self['武器列表'], 'ＥＮ', WEAPON_STRUCTURE['ＥＮ'])

        group_layout = QGridLayout()
        group_layout.addWidget(FontLabel('属性'), 0, 0, 1, 1)
        group_layout.addWidget(self['属性'], 0, 1, 1, 5)

        group_layout.addWidget(FontLabel('近射程'), 1, 0, 1, 1)
        group_layout.addWidget(self['近射程'], 1, 1, 1, 1)
        group_layout.addWidget(FontLabel('远射程'), 2, 0, 1, 1)
        group_layout.addWidget(self['远射程'], 2, 1, 1, 1)
        group_layout.addWidget(FontLabel('命中'), 3, 0, 1, 1)
        group_layout.addWidget(self['命中'], 3, 1, 1, 1)
        group_layout.addWidget(FontLabel('ＣＴ'), 4, 0, 1, 1)
        group_layout.addWidget(self['ＣＴ'], 4, 1, 1, 1)

        group_layout.addWidget(FontLabel('初期弹数'), 1, 2, 1, 1)
        group_layout.addWidget(self['初期弹数'], 1, 3, 1, 1)
        group_layout.addWidget(FontLabel('最大弹数'), 2, 2, 1, 1)
        group_layout.addWidget(self['最大弹数'], 2, 3, 1, 1)
        group_layout.addWidget(FontLabel('改造类型'), 3, 2, 1, 1)
        group_layout.addWidget(self['改造类型'], 3, 3, 1, 1)
        group_layout.addWidget(FontLabel('改造追加'), 4, 2, 1, 1)
        group_layout.addWidget(self['改造追加'], 4, 3, 1, 1)

        group_layout.addWidget(FontLabel('ＥＮ'), 1, 4, 1, 1)
        group_layout.addWidget(self['ＥＮ'], 1, 5, 1, 1)
        group_layout.addWidget(FontLabel('气力'), 2, 4, 1, 1)
        group_layout.addWidget(self['气力'], 2, 5, 1, 1)
        group_layout.addWidget(FontLabel('新人类'), 3, 4, 1, 1)
        group_layout.addWidget(self['新人类'], 3, 5, 1, 1)
        group_layout.addWidget(FontLabel('圣战士'), 4, 4, 1, 1)
        group_layout.addWidget(self['圣战士'], 4, 5, 1, 1)

        group.setLayout(group_layout)
        return group

    def init_weapon_map(self):
        group = FontGroup('地图武器')
        self['地图武器分类'] = RadioCombo(self['武器列表'], '地图武器分类', WEAPON_STRUCTURE['地图武器分类'],
                                    mapping=EnumData.WEAPON['地图武器分类'])
        self['地图武器演出'] = ValueSpin(self['武器列表'], '地图武器演出', WEAPON_STRUCTURE['地图武器演出'])
        self['着弹点指定型攻击半径'] = ValueSpin(self['武器列表'], '着弹点指定型攻击半径', WEAPON_STRUCTURE['着弹点指定型攻击半径'])
        self['方向指定型范围'] = RangeCombo(self['武器列表'], '方向指定型范围', WEAPON_STRUCTURE['方向指定型范围'])

        # noinspection PyUnresolvedReferences
        self['地图武器分类'].currentIndexChanged.connect(self.switch_maptype)
        self['地图武器演出'].setFixedSize(60, 28)
        self['着弹点指定型攻击半径'].setFixedSize(60, 28)

        group_layout = QGridLayout()
        group_layout.setObjectName('weapon_map')
        group_layout.addWidget(FontLabel('分类'), 0, 0, 1, 2)
        group_layout.addWidget(self['地图武器分类'], 1, 0, 1, 2)
        group_layout.addWidget(FontLabel('演出'), 2, 0, 1, 1)
        group_layout.addWidget(self['地图武器演出'], 2, 1, 1, 1)
        group_layout.addWidget(FontLabel('着弹点指定型攻击半径'), 3, 0, 1, 1)
        group_layout.addWidget(self['着弹点指定型攻击半径'], 3, 1, 1, 1)
        group_layout.addWidget(FontLabel('方向指定型范围'), 4, 0, 1, 1)
        group_layout.addWidget(self['方向指定型范围'], 5, 0, 1, 2)
        group_layout.addItem(QSpacerItem(1, 1, QSizePolicy.Fixed, QSizePolicy.Expanding), 6, 0, 1, 2)
        group.setLayout(group_layout)
        return group

    def init_weapon_adaptation(self):
        group = FontGroup('武器适应')
        self['空'] = MappingSpin(self['武器列表'], '空适应', WEAPON_STRUCTURE['空适应'], EnumData.WEAPON['適応'])
        self['陸'] = MappingSpin(self['武器列表'], '陆适应', WEAPON_STRUCTURE['陆适应'], EnumData.WEAPON['適応'])
        self['海'] = MappingSpin(self['武器列表'], '海适应', WEAPON_STRUCTURE['海适应'], EnumData.WEAPON['適応'])
        self['宇'] = MappingSpin(self['武器列表'], '宇适应', WEAPON_STRUCTURE['宇适应'], EnumData.WEAPON['適応'])
        group_layout = QFormLayout()
        group_layout.addRow(FontLabel('空适应'), self['空'])
        group_layout.addRow(FontLabel('陆适应'), self['陸'])
        group_layout.addRow(FontLabel('海适应'), self['海'])
        group_layout.addRow(FontLabel('宇适应'), self['宇'])
        group.setLayout(group_layout)
        return group

    def switch_maptype(self):
        # noinspection PyTypeChecker
        layout: QGridLayout = self.findChild(QGridLayout, 'weapon_map')
        if self['地图武器分类'].currentIndex() == 0:
            layout.itemAtPosition(2, 0).widget().setHidden(True)
            layout.itemAtPosition(3, 0).widget().setHidden(True)
            layout.itemAtPosition(4, 0).widget().setHidden(True)
            self['地图武器演出'].setHidden(True)
            self['着弹点指定型攻击半径'].setHidden(True)
            self['方向指定型范围'].setHidden(True)
        elif self['地图武器分类'].currentIndex() == 1:
            layout.itemAtPosition(2, 0).widget().setHidden(False)
            layout.itemAtPosition(3, 0).widget().setHidden(True)
            layout.itemAtPosition(4, 0).widget().setHidden(False)
            self['地图武器演出'].setHidden(False)
            self['着弹点指定型攻击半径'].setHidden(True)
            self['方向指定型范围'].setHidden(False)
        elif self['地图武器分类'].currentIndex() == 2:
            layout.itemAtPosition(2, 0).widget().setHidden(False)
            layout.itemAtPosition(3, 0).widget().setHidden(True)
            layout.itemAtPosition(4, 0).widget().setHidden(True)
            self['地图武器演出'].setHidden(False)
            self['着弹点指定型攻击半径'].setHidden(True)
            self['方向指定型范围'].setHidden(True)
        elif self['地图武器分类'].currentIndex() == 3:
            layout.itemAtPosition(2, 0).widget().setHidden(False)
            layout.itemAtPosition(3, 0).widget().setHidden(False)
            layout.itemAtPosition(4, 0).widget().setHidden(True)
            self['地图武器演出'].setHidden(False)
            self['着弹点指定型攻击半径'].setHidden(False)
            self['方向指定型范围'].setHidden(True)

    def set_roms(self, roms: list[RobotRAF]):
        self.rom = roms[0]
        self.parse()

    def parse(self):
        self.rom.parse()
        # noinspection PyUnresolvedReferences
        self['分离机体'].init_mapping(self.robots | {0xFFFF: 'ーー'})
        self['机体列表'].install(self.rom.data)
        self.switch_maptype()

        self.original_data = deepcopy(self.rom.data)

    def build(self):
        self.rom.build()

    def builded(self) -> bool:
        if self.original_data == self.rom.data:
            return True
        return False
