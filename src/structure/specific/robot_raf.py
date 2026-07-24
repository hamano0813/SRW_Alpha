#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parameter import HALF_TEXT_EXTRA
from structure.destructor import ROBOT
from structure.generic import Rom, Value, Text, Sequence

WEAPON_STRUCTURE = {
    '代码': Value(0x0, 0x1, (0, 4)),
    '新人类': Value(0x0, 0x1, (4, 6)),
    '圣战士': Value(0x0, 0x1, (6, 8)),
    '气力': Value(0x1, 0x1),
    '改造类型': Value(0x2, 0x1, (0, 2)),
    '近射程': Value(0x2, 0x1, (2, 4)),
    '远射程': Value(0x2, 0x1, (4, 8)),
    '地图武器分类': Value(0x3, 0x1, (0, 2)),
    '着弹点指定型攻击半径': Value(0x3, 0x1, (2, 5)),
    '攻击力': Value(0x4, 0x2),
    '分类': Value(0x6, 0x1, 0),
    '属性': Value(0x6, 0x1, (1, 8)),
    '改造追加': Value(0x7, 0x1, (4, 8)),
    '武器': Text(0x8, 0x15, 'shiftjisx0213', HALF_TEXT_EXTRA),
    '方向指定型范围': Value(0x1D, 0x1),
    '地图武器演出': Value(0x1E, 0x1),
    'ＥＮ': Value(0x1F, 0x1),
    '命中': Value(0x20, -0x1),
    'ＣＴ': Value(0x21, -0x1),
    '初期弹数': Value(0x22, 0x1),
    '最大弹数': Value(0x23, 0x1),
    '空适应': Value(0x24, 0x1),
    '陆适应': Value(0x25, 0x1),
    '海适应': Value(0x26, 0x1),
    '宇适应': Value(0x27, 0x1),
}

ROBOT_STRUCTURE = {
    '机体': Text(0x0, 0x1A, 'shiftjisx0213', HALF_TEXT_EXTRA),
    '代码': Value(0x1A, 0x2),
    '移动类型': Value(0x1C, 0x1, (0, 4)),
    '移动力': Value(0x1D, 0x1),
    'ＨＰ': Value(0x1E, 0x2),
    'ＥＮ': Value(0x20, 0x2),
    '运动性': Value(0x22, 0x2),
    '装甲': Value(0x24, 0x2),
    '限界': Value(0x26, 0x2),
    '体积': Value(0x28, 0x1),
    '芯片': Value(0x29, 0x1),
    '换乘系': Value(0x2A, 0x2, (0, 10)),
    '特性': Value(0x2C, 0x4, (0, 31)),
    '修理费': Value(0x30, 0x2),
    '资金': Value(0x32, 0x2),
    '变形组号': Value(0x34, 0x1),
    '变形序号': Value(0x35, 0x1),
    '合体组号': Value(0x36, 0x1),
    '合体序号': Value(0x37, 0x1),
    '分离机体': Value(0x38, 0x2),
    '合体数': Value(0x3A, 0x1),
    '换装系统': Value(0x3B, 0x1),
    '机体BGM': Value(0x3C, 0x1),
    '空适应': Value(0x40, 0x1),
    '陆适应': Value(0x41, 0x1),
    '海适应': Value(0x42, 0x1),
    '宇适应': Value(0x43, 0x1),
    '武器列表': Sequence(WEAPON_STRUCTURE, 0x44, 0x28, 0x10),
}


class RobotRAF(Rom):
    def __init__(self):
        super(RobotRAF, self).__init__()

    def parse(self) -> bool:
        if not self.buffer:
            return False
        self.data = ROBOT.parse(self.buffer, HALF_TEXT_EXTRA, dict())
        return True

    def build(self) -> bool:
        if not self.data:
            return False
        self.buffer = ROBOT.build(self.data, {v: k for k, v in reversed(HALF_TEXT_EXTRA.items())}, dict())
        return True

    def robots(self) -> dict[int, str]:
        if not self.data:
            return dict()
        return {idx: f"[{idx:03X}]{node['机体']}" for idx, node in enumerate(self.data['机体列表'])}
