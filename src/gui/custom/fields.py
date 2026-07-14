"""
ROM 数据结构映射模块

定义各 ROM 文件的二进制字段与编辑字段名之间的映射关系。
支持机器人、武器、驾驶员、技能、消息、脚本等数据类型的映射。

Classes:
    MappingType: 数据结构映射，提供字段名转换字典
"""

from PySide6.QtCore import QObject


class MappingType(QObject):
    """ROM 数据结构字段映射"""

    def __init__(self):
        super().__init__()
        self._mapping = {}
        self.update_mapping()

    def update_mapping(self):
        for mapping in [
            # ROBOT_RAF
            self._init_robot(),
            self._init_weapon(),
            # PILOT_BIN
            self._init_pilot(),
            self._init_skill(),
            # DC_BIN
            self._init_character(),
            # SNMSG_BIN
            self._init_snmsg(),
            # SNDATA_BIN
            self._init_sndata(),
            self._init_scenario(),
            self._init_command(),
            # SCRIPT_BIN
            self._init_script(),
            # AIUNP_BIN
            self._init_aiunp(),
            # Unknown
            self._init_unknown(),
        ]:
            for key, value in mapping.items():
                if key not in self._mapping:
                    self._mapping[key] = value
                elif self._mapping[key] != value:
                    raise ValueError(f"Duplicate key with different values: {key}")

    def _init_robot(self):
        mapping = {
            self.tr("robot name"): "rname",
            self.tr("code"): "code",
            self.tr("movement type"): "type",
            self.tr("movement"): "move",
            self.tr("hit points"): "hp",
            self.tr("energy"): "en",
            self.tr("mobility"): "mobility",
            self.tr("armor"): "armor",
            self.tr("limit"): "limit",
            self.tr("size"): "size",
            self.tr("parts slot"): "slot",
            self.tr("series"): "series",
            self.tr("abilities"): "abi",
            self.tr("repair cost"): "rep",
            self.tr("cost"): "cost",
            self.tr("transform group number"): "tgrp",
            self.tr("transform sequence number"): "tsn",
            self.tr("combine group number"): "cgrp",
            self.tr("combine sequence number"): "csn",
            self.tr("core robot"): "core",
            self.tr("combine count"): "count",
            self.tr("option parts system"): "option",
            self.tr("background music"): "bgm",
            self.tr("air"): "air",
            self.tr("ground"): "grd",
            self.tr("water"): "wtr",
            self.tr("space"): "spc",
            self.tr("weapons"): "weapons",
        }
        return mapping

    def _init_weapon(self):
        mapping = {
            self.tr("code"): "code",
            self.tr("required newtype level"): "newtype",
            self.tr("required aura level"): "aura",
            self.tr("required morale value"): "morale",
            self.tr("custom type"): "custom",
            self.tr("short range"): "rngs",
            self.tr("long range"): "rngl",
            self.tr("map weapon class"): "mcls",
            self.tr("map weapon radius"): "radius",
            self.tr("damage"): "damage",
            self.tr("weapon class"): "class",
            self.tr("attribute"): "attr",
            self.tr("custom bonus"): "bonus",
            self.tr("weapon name"): "wname",
            self.tr("map weapon range"): "mrng",
            self.tr("map weapon show"): "mshow",
            self.tr("energy cost"): "encost",
            self.tr("hit rate"): "hitrate",
            self.tr("critical rate"): "crt",
            self.tr("default ammo"): "ammod",
            self.tr("maximum ammo"): "ammom",
            self.tr("air"): "air",
            self.tr("ground"): "grd",
            self.tr("water"): "wtr",
            self.tr("space"): "spc",
        }
        return mapping

    def _init_pilot(self):
        mapping = {
            self.tr("code"): "code",
            self.tr("series"): "series",
            self.tr("fullname"): "fname",
            self.tr("nickname"): "nname",
            self.tr("combat"): "cqb",
            self.tr("ranged"): "rng",
            self.tr("evasion"): "evd",
            self.tr("accuracy"): "hit",
            self.tr("reaction"): "rxn",
            self.tr("skill"): "skl",
            self.tr("spirit commands"): "spi",
            self.tr("spirit level"): "spl",
            self.tr("upgraded skills"): "sklu",
            self.tr("SP"): "sp",
            self.tr("double action"): "daction",
            self.tr("special skills"): "skls",
            self.tr("nature"): "nature",
            self.tr("friendship group"): "fsg",
            self.tr("air"): "air",
            self.tr("ground"): "grd",
            self.tr("water"): "wtr",
            self.tr("space"): "spc",
        }
        return mapping

    def _init_character(self):
        mapping = {
            self.tr("full name"): "fname",
            self.tr("pet name"): "pname",
            self.tr("appearance"): "appr",
            self.tr("voice actor"): "voice",
            self.tr("flags"): "flags",
            self.tr("description"): "desc",
        }
        return mapping

    def _init_skill(self):
        mapping = {
            self.tr("skill name"): "sname",
            self.tr("skill level1"): "l1",
            self.tr("skill level2"): "l2",
            self.tr("skill level3"): "l3",
            self.tr("skill level4"): "l4",
            self.tr("skill level5"): "l5",
            self.tr("skill level6"): "l6",
            self.tr("skill level7"): "l7",
            self.tr("skill level8"): "l8",
            self.tr("skill level9"): "l9",
        }
        return mapping

    def _init_sndata(self):
        mapping = {
            self.tr("scenario pointer"): "sptr",
            self.tr("scenario data"): "sndata",
        }
        return mapping

    def _init_scenario(self):
        mapping = {
            self.tr("block count"): "bcount",
            self.tr("block length"): "blen",
            self.tr("block pointers"): "bptrs",
            self.tr("command data"): "cdata",
        }
        return mapping

    def _init_command(self):
        mapping = {
            self.tr("command code"): "ccode",
            self.tr("command count"): "ccount",
            self.tr("command params"): "cparams",
        }
        return mapping

    def _init_snmsg(self):
        mapping = {
            self.tr("message"): "msg",
        }
        return mapping

    def _init_script(self):
        mapping = {
            self.tr("script command"): "scmd",
            self.tr("script params1"): "sparams1",
            self.tr("script params2"): "sparams2",
            self.tr("script expand"): "sexpand",
        }
        return mapping

    def _init_aiunp(self):
        mapping = {
            self.tr("ai pointers"): "aiptrs",
            self.tr("ai data"): "aidata",
            self.tr("ai count"): "aicount",
            self.tr("ai length"): "ailen",
            self.tr("ai list"): "ailist",
            self.tr("AI"): "ai",
            self.tr("valid"): "valid",
            self.tr("move round"): "mrnd",
            self.tr("own move"): "omov",
            self.tr("own attack"): "oatk",
            self.tr("target pilot"): "tpil",
            self.tr("target x"): "tx",
            self.tr("target y"): "ty",
        }
        return mapping

    def _init_unknown(self):
        mapping = {
            self.tr("unknown01"): "unk01",
            self.tr("unknown02"): "unk02",
            self.tr("unknown03"): "unk03",
            self.tr("unknown04"): "unk04",
            self.tr("unknown05"): "unk05",
            self.tr("unknown06"): "unk06",
            self.tr("unknown07"): "unk07",
            self.tr("unknown08"): "unk08",
            self.tr("unknown09"): "unk09",
            self.tr("unknown10"): "unk10",
            self.tr("unknown11"): "unk11",
            self.tr("unknown12"): "unk12",
            self.tr("unknown13"): "unk13",
            self.tr("unknown14"): "unk14",
            self.tr("unknown15"): "unk15",
            self.tr("unknown16"): "unk16",
            self.tr("unknown17"): "unk17",
            self.tr("unknown18"): "unk18",
            self.tr("unknown19"): "unk19",
            self.tr("unknown20"): "unk20",
            self.tr("unknown21"): "unk21",
            self.tr("unknown22"): "unk22",
            self.tr("unknown23"): "unk23",
            self.tr("unknown24"): "unk24",
            self.tr("unknown25"): "unk25",
            self.tr("unknown26"): "unk26",
            self.tr("unknown27"): "unk27",
            self.tr("unknown28"): "unk28",
            self.tr("unknown29"): "unk29",
            self.tr("unknown30"): "unk30",
            self.tr("unknown31"): "unk31",
            self.tr("unknown32"): "unk32",
            self.tr("unknown33"): "unk33",
            self.tr("unknown34"): "unk34",
            self.tr("unknown35"): "unk35",
            self.tr("unknown36"): "unk36",
            self.tr("unknown37"): "unk37",
            self.tr("unknown38"): "unk38",
            self.tr("unknown39"): "unk39",
            self.tr("unknown40"): "unk40",
            self.tr("unknown41"): "unk41",
            self.tr("unknown42"): "unk42",
            self.tr("unknown43"): "unk43",
            self.tr("unknown44"): "unk44",
            self.tr("unknown45"): "unk45",
            self.tr("unknown46"): "unk46",
            self.tr("unknown47"): "unk47",
            self.tr("unknown48"): "unk48",
            self.tr("unknown49"): "unk49",
            self.tr("unknown50"): "unk50",
        }
        return mapping
