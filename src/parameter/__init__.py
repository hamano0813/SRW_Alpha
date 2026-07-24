#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from parameter.enum_data import EnumDataTrans
from parameter.text_extra import HALF_TEXT_EXTRA, SNMSG_TEXT_EXTRA, SCRIPT_TEXT_EXTRA

EnumData = EnumDataTrans()

EVENT_PATH = r'event.txt'

if os.path.exists(EVENT_PATH):
    with open(EVENT_PATH, 'r', encoding='utf-8') as f:
        EnumData.EVENT = dict()
        for line in f.readlines():
            code, event = line.split('=')[0:2]
            EnumData.EVENT[int(code, 16)] = f'[{code}] {event.strip()}'
