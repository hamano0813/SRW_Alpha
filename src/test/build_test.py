#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import time

from structure import RobotRAF, PilotBIN, SnmsgBIN, SndataBIN, EnlistBIN, AiunpBIN, ScriptBIN, PrmgrpBIN

paths = {
    'ROBOT': '../../resource/bin/jp/UNCOMPRESS_ROBOT.RAF',
    'PILOT': '../../resource/bin/jp/PILOT.BIN',
    'SNMSG': '../../resource/bin/jp/SNMSG.BIN',
    'SNDATA': '../../resource/bin/jp/SNDATA.BIN',
    'ENLIST': '../../resource/bin/jp/ENLIST.BIN',
    'AIUNP': '../../resource/bin/jp/AIUNP.BIN',
    'SCRIPT': '../../resource/bin/jp/SCRIPT.BIN',
    'PRMGRP': '../../resource/bin/jp/PRM_GRP.BIN',
}

roms = {
    'ROBOT': RobotRAF,
    'PILOT': PilotBIN,
    'SNMSG': SnmsgBIN,
    'SNDATA': SndataBIN,
    'ENLIST': EnlistBIN,
    'AIUNP': AiunpBIN,
    'SCRIPT': ScriptBIN,
    'PRMGRP': PrmgrpBIN,
}

if __name__ == '__main__':
    for k, r in roms.items():
        rom = r()
        path = paths.get(k)
        parse_start = time.time()
        rom.load(path)
        parse_end = time.time()
        buf = copy.deepcopy(rom.buffer)
        data = copy.deepcopy(rom.data)
        build_start = time.time()
        rom.build()
        build_end = time.time()
        rom.parse()

        if buf == rom.buffer:
            result = "buffer successful!"
        elif data == rom.data:
            result = "  data successful!"
        else:
            result = "failed!"

        parse_time = parse_end - parse_start
        build_time = build_end - build_start
        print(f'{r.__name__:<10s} {result:<12s}  '
              f'parse time {parse_time:.3f}s, '
              f'build time {build_time:.3f}s, '
              f'total time {parse_time + build_time:.3f}s')

        # for si, s in enumerate(rom.data['剧本列表']):
        #     for ci, c in enumerate(s['指令列表']):
        #         if c['指令码'] == 0x4000:
        #             print(hex(si), ci, *c.values(), sep='\t')
        #             # print(hex(si), ci + 1, s['指令列表'][ci + 1])
