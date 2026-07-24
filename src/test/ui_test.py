#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

import parameter
from interface.main_window import MainWindow

parameter.EVENT_PATH = EVENT_PATH = r'..\event.txt'
if os.path.exists(EVENT_PATH):
    with open(EVENT_PATH, 'r', encoding='utf-8') as f:
        parameter.EnumData.EVENT = dict()
        for line in f.readlines():
            code, event = line.split('=')[0:2]
            parameter.EnumData.EVENT[int(code, 16)] = f'[{code}] {event.strip()}'

lang = 'jp'

if __name__ == '__main__':
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    w = MainWindow()
    w.roms['UNCOMPRESS_ROBOT.RAF'].load(rf'..\..\resource\bin\{lang}\UNCOMPRESS_ROBOT.RAF')
    w.roms['PILOT.BIN'].load(rf'..\..\resource\bin\{lang}\PILOT.BIN')
    w.roms['SNMSG.BIN'].load(rf'..\..\resource\bin\{lang}\SNMSG.BIN')
    w.roms['SNDATA.BIN'].load(rf'..\..\resource\bin\{lang}\SNDATA.BIN')
    w.roms['ENLIST.BIN'].load(rf'..\..\resource\bin\{lang}\ENLIST.BIN')
    w.roms['AIUNP.BIN'].load(rf'..\..\resource\bin\{lang}\AIUNP.BIN')
    w.roms['SCRIPT.BIN'].load(rf'..\..\resource\bin\{lang}\SCRIPT.BIN')
    w.roms['PRM_GRP.BIN'].load(rf'..\..\resource\bin\{lang}\PRM_GRP.BIN')
    w.check_enable()
    w.show()
    sys.exit(app.exec())
