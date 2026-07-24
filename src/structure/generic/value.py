#!/usr/bin/env python
# -*- coding: utf-8 -*-

from struct import unpack_from, pack_into


class Value:
    length_format = {0x1: 'B', 0x2: 'H', 0x4: 'I', 0x8: 'Q', -0x1: 'b', -0x2: 'h', -0x4: 'i', -0x8: 'q'}

    def __init__(self, offset: int, length: int, bit=None):
        self.offset = offset
        self.length = length
        self.fmt = self.length_format[length]
        self.bit: int | tuple = bit

    def parse(self, buffer: bytearray) -> int:
        data = unpack_from(self.fmt, buffer, self.offset)[0]
        if self.bit is not None:
            return self._load_bin(data)
        return data

    def build(self, value: int, buffer: bytearray) -> bytearray:
        if self.bit is not None:
            data = self._save_bin(unpack_from(self.fmt, buffer, self.offset)[0], value)
        else:
            data = value
        pack_into(self.fmt, buffer, self.offset, data)
        return buffer

    def _load_bin(self, value: int) -> int:
        if isinstance(self.bit, int):
            return (value & (1 << self.bit)) >> self.bit
        _value = (value & ((1 << self.bit[1]) - 1)) >> self.bit[0]
        if self.length > 0:
            return _value
        bit_width = self.bit[1] - self.bit[0] - 1
        return (_value & ((1 << bit_width) - 1)) - (_value & (1 << bit_width))

    def _save_bin(self, data: int, value: int) -> int:
        if isinstance(self.bit, int):
            return data | (1 << self.bit) if value else data & ~ (1 << self.bit)
        if value < 0:
            value += (1 << (self.bit[1] - self.bit[0]))
        return ((data >> self.bit[1]) << self.bit[1]) | (data & ((1 << self.bit[0]) - 1)) | (value << self.bit[0])
