#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Optional

from structure.generic.text import Text
from structure.generic.value import Value

SEQUENCE = list[dict[str, int | str | Optional["SEQUENCE"]]]


class Sequence:
    def __init__(self, structures, offset: int, length: int, count: int = 0x1):
        self.structures: dict[str, Value | Text | Optional["Sequence"]] = structures
        self.offset = offset
        self.length = length
        self.count = count

    def parse(self, buffer: bytearray) -> SEQUENCE:
        sequence = list()
        for idx in range(self.count):
            record = dict()
            _buffer = buffer[self._idx_range(idx)]
            for pname, structure in self.structures.items():
                record[pname] = structure.parse(_buffer)
            sequence.append(record)
        return sequence

    def build(self, sequence: SEQUENCE, buffer: bytearray) -> bytearray:
        for idx, record in enumerate(sequence):
            _buffer = buffer[self._idx_range(idx)]
            for key, data in record.items():
                if structure := self.structures.get(key):
                    structure.build(data, _buffer)
            buffer[self._idx_range(idx)] = _buffer
        return buffer

    def _idx_range(self, idx: int) -> slice:
        return slice(self.offset + self.length * idx, self.offset + self.length * (idx + 1))

    def __getitem__(self, item: str):
        return self.structures.get(item)
