#!/usr/bin/env python
# -*- coding: utf-8 -*-

from structure.destructor import SNDATA
from structure.generic import Rom


class SndataBIN(Rom):
    def __init__(self):
        super(SndataBIN, self).__init__()

    def parse(self) -> bool:
        if not self.buffer:
            return False
        self.data = SNDATA.parse(self.buffer)
        return True

    def build(self) -> bool:
        if not self.data:
            return False
        self.buffer = SNDATA.build(self.data)
        return True
