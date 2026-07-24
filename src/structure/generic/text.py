#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
from struct import unpack_from, pack_into


class Text:
    def __init__(self, offset: int, length: int, code: str, extra: dict = None, dummy: bytearray = None):
        self.offset = offset
        self.length = length
        self.code = code
        self.extra = extra
        self.dummy = dummy

    def parse(self, buffer: bytearray) -> str:
        data = unpack_from(f'{self.length}s', buffer, self.offset)[0].split(b'\00')[0]
        return self._decode_text(data)

    def build(self, text: str, buffer: bytearray) -> bytearray:
        data = self._encode_text(text)[:self.length]
        if self.dummy:
            _buffer = copy.deepcopy(self.dummy)
        else:
            _buffer = bytearray(self.length)
        _buffer[0: len(data)] = data
        pack_into(f'{self.length}s', buffer, self.offset, _buffer)
        return buffer

    def _decode_text(self, data: bytes) -> str:
        temp = data.decode(self.code, 'replace')
        if self.extra:
            for old, new in self.extra.items():
                temp = temp.replace(old, new)
        return temp

    def _encode_text(self, text: str) -> bytearray:
        temp = text
        if self.extra:
            for old, new in reversed(self.extra.items()):
                temp = temp.replace(new, old)
        return bytearray(temp.encode(self.code))
