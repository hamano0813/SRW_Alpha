#!/usr/bin/env python
# -*- coding: utf-8 -*-

from parameter import SCRIPT_TEXT_EXTRA
from structure.destructor import SCRIPT
from structure.generic import Rom


class ScriptBIN(Rom):
    def __init__(self):
        super(ScriptBIN, self).__init__()

    def parse(self) -> bool:
        if not self.buffer:
            return False
        self.data = SCRIPT.parse(self.buffer, SCRIPT_TEXT_EXTRA, dict())
        return True

    def build(self) -> bool:
        if not self.data:
            return False
        self.buffer = SCRIPT.build(self.data, {v: k for k, v in reversed(SCRIPT_TEXT_EXTRA.items())}, dict())
        return True
