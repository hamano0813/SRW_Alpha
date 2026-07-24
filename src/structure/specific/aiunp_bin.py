#!/usr/bin/env python
# -*- coding: utf-8 -*-

from structure.generic import Rom, Value, Sequence, SEQUENCE

AI_STRUCTURE = {
    'AI': Value(0x0, 0x2),
    '不明10': Value(0x2, 0x1, 0),
    '不明11': Value(0x2, 0x1, 1),
    '不明12': Value(0x2, 0x1, 2),
    '不明13': Value(0x2, 0x1, 3),
    '不明14': Value(0x2, 0x1, 4),
    '不明15': Value(0x2, 0x1, 5),
    '不明16': Value(0x2, 0x1, 6),
    '不明17': Value(0x2, 0x1, 7),
    '不明2': Value(0x3, 0x1),
    '不明30': Value(0x4, 0x1, 0),
    '不明31': Value(0x4, 0x1, 1),
    '不明32': Value(0x4, 0x1, 2),
    '不明33': Value(0x4, 0x1, 3),
    '不明34': Value(0x4, 0x1, 4),
    '不明35': Value(0x4, 0x1, 5),
    '不明36': Value(0x4, 0x1, 6),
    '不明37': Value(0x4, 0x1, 7),
    '生效': Value(0x5, 0x1, 0),
    '移动开始': Value(0x5, 0x1, (1, 4)),
    '不明44': Value(0x5, 0x1, 4),
    '自主移动': Value(0x5, 0x1, 5),
    '不明46': Value(0x5, 0x1, 6),
    '自主攻击': Value(0x5, 0x1, 7),
    '目标机师': Value(0x6, 0x2),
    '目标X': Value(0x8, 0x1),
    '目标Y': Value(0x9, 0x1),
}

SETTING_STRUCTURE = {
    '空': Value(0x0, 0x2),
    'AI数量': Value(0x2, 0x2),
    'AI长度': Value(0x4, 0x2),
    'AI列表': Sequence(AI_STRUCTURE, 0x6, 0xA, 0x0)
}


class AiSetting(Sequence):
    def __init__(self, structures, offset, length, count):
        super(AiSetting, self).__init__(structures, offset, length, count)
        self.pointers: list[dict[str, int]] = list()

    def parse(self, buffer: bytearray) -> SEQUENCE:
        sequence = list()
        for idx in range(self.count):
            record = dict()
            _buffer = buffer[self._idx_range(idx)]
            record['空'] = self.structures['空'].parse(_buffer)
            record['AI数量'] = self.structures['AI列表'].count = self.structures['AI数量'].parse(_buffer)
            record['AI长度'] = self.structures['AI长度'].parse(_buffer)
            record['AI列表'] = self.structures['AI列表'].parse(_buffer)
            sequence.append(record)
        return sequence

    def build(self, sequence: SEQUENCE, buffer: bytearray) -> bytearray:
        for idx, record in enumerate(sequence):
            count = self.structures['AI列表'].count = record['AI数量'] = len(record['AI列表'])
            length = self._calc_length(0xA * count + 0x6)
            self.pointers[idx + 1]['指针'] = self.pointers[idx]['指针'] + length
            _buffer = bytearray(length)
            for key, data in record.items():
                self.structures[key].build(data, _buffer)
            buffer[self._idx_range(idx)] = _buffer
        return buffer

    def _idx_range(self, idx: int) -> slice:
        return slice(self.pointers[idx]['指针'], self.pointers[idx + 1]['指针'])

    @staticmethod
    def _calc_length(value: int, step: int = 0x4) -> int:
        return (value // step + bool(value % step)) * step


class AiunpBIN(Rom):
    def __init__(self):
        super(AiunpBIN, self).__init__()
        self.structures = {
            '指针列表': Sequence({'指针': Value(0x0, 0x4)}, 0x0, 0x4, 0x8D),
            'AI设计': AiSetting(SETTING_STRUCTURE, 0x800, 0x0, 0x8C),
        }

    def parse(self) -> bool:
        if not self.buffer:
            return False
        self['指针列表'] = self.structures['AI设计'].pointers = self.structures['指针列表'].parse(self.buffer)
        self['AI设计'] = self.structures['AI设计'].parse(self.buffer)
        return True
