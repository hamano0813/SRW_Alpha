"""
ROM 数据结构映射模块

定义各 ROM 文件的二进制字段与编辑字段名之间的映射关系。
支持机器人、武器、驾驶员、技能、消息、脚本等数据类型的映射。

Classes:
    FieldMapping: 字段映射类，提供字段名转换字典
"""

from PySide6.QtCore import QObject


class FieldMapping(QObject):
    """ROM 数据结构字段映射

    构造时自动合并各 _init_* 方法返回的映射表，冲突键抛出 ValueError。
    可在运行期重复调用 update_mapping() 刷新。
    """

    def __init__(self):
        """初始化字段映射，合并各数据类型的字段定义"""
        super().__init__()
        self.update_mapping()

    def update_mapping(self):
        """重建映射表，合并所有 _init_* 方法返回的字段定义

        冲突键（同 key 不同 value）抛出 ValueError。
        可在运行期重复调用以刷新翻译。
        """
        self._mapping = {}
        for mapping in [
            # ROBOT_RAF
            self._init_robot(),
            self._init_weapon(),
            # PILOT_BIN
            self._init_pilot(),
            self._init_skill(),
            # DC_BIN
            self._init_dc(),
            # DR_BIN
            self._init_dr(),
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

    # ========== 各类数据字段定义 ==========

    def _init_robot(self):
        """ROBOT.RAF 机体数据结构字段"""
        mapping = {
            self.tr("Robot name"): "rname",  # 机体 / ユニット
            self.tr("Code"): "code",  # 编码 / コード
            self.tr("Movement type"): "type",  # 移动类型 / 移動タイプ
            self.tr("Movement"): "move",  # 移动力 / 移動力
            self.tr("Hit points"): "hp",  # HP / HP
            self.tr("Energy"): "en",  # EN / EN
            self.tr("Mobility"): "mobility",  # 运动性 / 運動性
            self.tr("Armor"): "armor",  # 装甲 / 装甲
            self.tr("Limit"): "limit",  # 限界 / 限界
            self.tr("Size"): "size",  # 体积 / サイズ
            self.tr("Parts slot"): "slot",  # 零件插槽 / パーツスロット
            self.tr("Series"): "series",  # 换乘系 / のりかえ系
            self.tr("Abilities"): "abi",  # 特殊能力 / 特殊能力
            self.tr("Repair cost"): "rep",  # 修理费 / 修理費
            self.tr("Cost"): "cost",  # 资金 / 資金
            self.tr("Tran Grp"): "tgrp",  # 变形组号 / 変形グループ
            self.tr("Tran Seq"): "tsn",  # 变形序号 / 変形シーケンス
            self.tr("Comb Grp"): "cgrp",  # 合体组号 / 合体グループ
            self.tr("Comb Seq"): "csn",  # 合体序号 / 合体シーケンス
            self.tr("Core Unit"): "core",  # 核心机体 / コアユニット
            self.tr("Comb Cnt"): "count",  # 合体数量 / 合体数
            self.tr("Option parts system"): "option",  # 机体换装 / ユニット換装
            self.tr("Background music"): "bgm",  # BGM / BGM
            self.tr("Air"): "air",  # 空 / 空
            self.tr("Ground"): "grd",  # 陆 / 陸
            self.tr("Water"): "wtr",  # 海 / 海
            self.tr("Space"): "spc",  # 宇 / 宇
            self.tr("Weapons"): "weapons",  # 武器列表 / 武器リスト
        }
        return mapping

    def _init_weapon(self):
        """ROBOT.RAF 武器数据结构字段"""
        mapping = {
            self.tr("Code"): "code",  # 编码 / コード
            self.tr("Required newtype level"): "newtype",  # 新人类等级 / ニュータイプレベル
            self.tr("Required aura level"): "aura",  # 圣战士等级 / 聖戦士レベル
            self.tr("Required morale value"): "morale",  # 必要气力 / 必要気力
            self.tr("Custom type"): "custom",  # 改造类型 / 改造タイプ
            self.tr("Short range"): "rngs",  # 近射程 / 近射程
            self.tr("Long range"): "rngl",  # 远射程 / 遠射程
            self.tr("Map weapon class"): "mcls",  # 地图武器分类 / マップ兵器分類
            self.tr("Map weapon radius"): "radius",  # 着弹指定型半径 / 着弾指定型半径
            self.tr("Damage"): "damage",  # 攻击力 / 攻撃力
            self.tr("Weapon class"): "class",  # 武器分类 / 武器分類
            self.tr("Attribute"): "attr",  # 属性 / 属性
            self.tr("Custom bonus"): "bonus",  # 改造追加 / 改造ボーナス
            self.tr("Weapon name"): "wname",  # 武器名 / 武器名
            self.tr("Map weapon range"): "mrng",  # 方向指定型范围 / 方向指定型範囲
            self.tr("Map weapon show"): "mshow",  # 地图武器演出 / マップ兵器演出
            self.tr("Energy cost"): "encost",  # 消耗EN / 消費EN
            self.tr("Accuracy"): "hit",  # 命中 / 命中
            self.tr("Critical"): "crt",  # 会心补正 / クリティカル補正
            self.tr("Default ammo"): "ammod",  # 初始弹药 / 初期弾数
            self.tr("Maximum ammo"): "ammom",  # 最大弹药 / 最大弾数
            self.tr("Air"): "air",  # 空 / 空
            self.tr("Ground"): "grd",  # 陆 / 陸
            self.tr("Water"): "wtr",  # 海 / 海
            self.tr("Space"): "spc",  # 宇 / 宇
        }
        return mapping

    def _init_pilot(self):
        """PILOT.BIN 驾驶员数据结构字段"""
        mapping = {
            self.tr("Code"): "code",  # 编码 / コード
            self.tr("Series"): "series",  # 换乘系 / のりかえ系
            self.tr("Fullname"): "fname",  # 全名 / 名前
            self.tr("Nickname"): "nname",  # 机师 / パイロット
            self.tr("Combat"): "cqb",  # 格斗 / 格闘
            self.tr("Ranged"): "rng",  # 射击 / 射撃
            self.tr("Evasion"): "evd",  # 回避 / 回避
            self.tr("Accuracy"): "hit",  # 命中 / 命中
            self.tr("Reaction"): "rxn",  # 反应 / 反応
            self.tr("Skill"): "skl",  # 技量 / 技量
            self.tr("Spirit commands"): "spi",  # 精神指令 / 精神コマンド
            self.tr("Spirit level"): "spl",  # 习得等级 / 習得レベル
            self.tr("Upgraded skills"): "sklu",  # 等级制技能 / レベル制技能
            self.tr("SP"): "sp",  # SP / SP
            self.tr("Double action"): "daction",  # 2次行动 / 2回行動
            self.tr("Special skills"): "skls",  # 特殊技能 / 特殊技能
            self.tr("Nature"): "nature",  # 性格 / 性格
            self.tr("Friendship group"): "fsg",  # 气力组 / 気力グループ
            self.tr("Air"): "air",  # 空 / 空
            self.tr("Ground"): "grd",  # 陆 / 陸
            self.tr("Water"): "wtr",  # 海 / 海
            self.tr("Space"): "spc",  # 宇 / 宇
        }
        return mapping

    def _init_skill(self):
        """PILOT.BIN 特殊技能数据结构字段"""
        mapping = {
            self.tr("Skill name"): "sname",  # 技能 / スキル
            self.tr("Skill level1"): "l1",  # Lv1 / Lv1
            self.tr("Skill level2"): "l2",  # Lv2 / Lv2
            self.tr("Skill level3"): "l3",  # Lv3 / Lv3
            self.tr("Skill level4"): "l4",  # Lv4 / Lv4
            self.tr("Skill level5"): "l5",  # Lv5 / Lv5
            self.tr("Skill level6"): "l6",  # Lv6 / Lv6
            self.tr("Skill level7"): "l7",  # Lv7 / Lv7
            self.tr("Skill level8"): "l8",  # Lv8 / Lv8
            self.tr("Skill level9"): "l9",  # Lv9 / Lv9
        }
        return mapping

    def _init_dc(self):
        """DC.BIN 人物图鉴数据结构字段"""
        mapping = {
            self.tr("Full name"): "fname",  # 全名 / フルネーム
            self.tr("Pet name"): "pname",  # 爱称 / 愛称
            self.tr("Appearance"): "appr",  # 登场作品 / 登場作品
            self.tr("Voice actor"): "voice",  # 声优 / 声優
            self.tr("Flags"): "flags",  # 标志 / フラグ
            self.tr("Description"): "desc",  # 事典 / 事典
        }
        return mapping

    def _init_dr(self):
        """DR.BIN 机体图鉴数据结构字段"""
        mapping = {
            self.tr("Name"): "name",  # 名称 / 名称
            self.tr("Height"): "height",  # 全长 / 全長
            self.tr("Weight"): "weight",  # 重量 / 重量
            self.tr("Appearance"): "appr",  # 登场作品 / 登場作品
            self.tr("Flags"): "flags",  # 标志 / フラグ
            self.tr("Description"): "desc",  # 介绍 / 紹介
        }
        return mapping

    def _init_sndata(self):
        """SNDATA.BIN 场景索引数据结构字段"""
        mapping = {
            self.tr("Scenario pointer"): "sptr",  # 场景指针 / シナリオポインタ
            self.tr("Scenario data"): "sndata",  # 场景数据 / シナリオデータ
        }
        return mapping

    def _init_scenario(self):
        """SNDATA.BIN 关卡指令块数据结构字段"""
        mapping = {
            self.tr("Block count"): "bcount",  # 块数量 / ブロック数
            self.tr("Block length"): "blen",  # 块长度 / ブロック長
            self.tr("Block pointers"): "bptrs",  # 块指针 / ブロックポインタ
            self.tr("Command data"): "cdata",  # 指令数据 / コマンドデータ
        }
        return mapping

    def _init_command(self):
        """SNDATA.BIN 单条指令数据结构字段"""
        mapping = {
            self.tr("Command code"): "ccode",  # 指令代码 / コマンドコード
            self.tr("Command count"): "ccount",  # 指令计数 / コマンド数
            self.tr("Command params"): "cparams",  # 指令参数 / コマンドパラメータ
            self.tr("Command explain"): "explain",  # 指令说明 / コマンド説明
        }
        return mapping

    def _init_snmsg(self):
        """SNMSG.BIN 消息数据结构字段"""
        mapping = {
            self.tr("Scenario Message"): "snmsg",  # 剧情文本 / シナリオメッセージ
        }
        return mapping

    def _init_script(self):
        """SCRIPT.BIN 脚本文本数据结构字段"""
        mapping = {
            self.tr("Script command"): "scmd",  # 剧本指令 / 脚本コマンド
            self.tr("Script params1"): "sparams1",  # 剧本参数1 / 脚本パラメータ1
            self.tr("Script params2"): "sparams2",  # 剧本参数2 / 脚本パラメータ2
            self.tr("Script expand"): "sexpand",  # 扩展文本 / 拡張テキスト
        }
        return mapping

    def _init_aiunp(self):
        """AIUNP.BIN AI 数据结构字段"""
        mapping = {
            self.tr("AI pointers"): "aiptrs",  # AI 指针 / AIポインタ
            self.tr("AI data"): "aidata",  # AI 数据 / AIデータ
            self.tr("AI count"): "aicount",  # AI 数量 / AI数
            self.tr("AI length"): "ailen",  # AI 长度 / AI長
            self.tr("AI list"): "ailist",  # AI 列表 / AIリスト
            self.tr("AI"): "ai",  # AI / AI
            self.tr("Valid"): "valid",  # 有效 / 有効
            self.tr("Move round"): "mrnd",  # 开始移动回合 / 移動開始ラウンド
            self.tr("Own move"): "omov",  # 自主移动 / 自主移動
            self.tr("Own attack"): "oatk",  # 自主攻击 / 自主攻撃
            self.tr("Target pilot"): "tpil",  # 目标驾驶员 / 目標パイロット
            self.tr("Target x"): "tx",  # 目标X / 目標X
            self.tr("Target y"): "ty",  # 目标Y / 目標Y
        }
        return mapping

    def _init_unknown(self):
        """未知数据结构字段（占位）"""
        mapping = {
            self.tr("Unknown01"): "unk01",  # 未知01 / 未知01
            self.tr("Unknown02"): "unk02",  # 未知02 / 未知02
            self.tr("Unknown03"): "unk03",  # 未知03 / 未知03
            self.tr("Unknown04"): "unk04",  # 未知04 / 未知04
            self.tr("Unknown05"): "unk05",  # 未知05 / 未知05
            self.tr("Unknown06"): "unk06",  # 未知06 / 未知06
            self.tr("Unknown07"): "unk07",  # 未知07 / 未知07
            self.tr("Unknown08"): "unk08",  # 未知08 / 未知08
            self.tr("Unknown09"): "unk09",  # 未知09 / 未知09
            self.tr("Unknown10"): "unk10",  # 未知10 / 未知10
            self.tr("Unknown11"): "unk11",  # 未知11 / 未知11
            self.tr("Unknown12"): "unk12",  # 未知12 / 未知12
            self.tr("Unknown13"): "unk13",  # 未知13 / 未知13
            self.tr("Unknown14"): "unk14",  # 未知14 / 未知14
            self.tr("Unknown15"): "unk15",  # 未知15 / 未知15
            self.tr("Unknown16"): "unk16",  # 未知16 / 未知16
            self.tr("Unknown17"): "unk17",  # 未知17 / 未知17
            self.tr("Unknown18"): "unk18",  # 未知18 / 未知18
            self.tr("Unknown19"): "unk19",  # 未知19 / 未知19
            self.tr("Unknown20"): "unk20",  # 未知20 / 未知20
            self.tr("Unknown21"): "unk21",  # 未知21 / 未知21
            self.tr("Unknown22"): "unk22",  # 未知22 / 未知22
            self.tr("Unknown23"): "unk23",  # 未知23 / 未知23
            self.tr("Unknown24"): "unk24",  # 未知24 / 未知24
            self.tr("Unknown25"): "unk25",  # 未知25 / 未知25
            self.tr("Unknown26"): "unk26",  # 未知26 / 未知26
            self.tr("Unknown27"): "unk27",  # 未知27 / 未知27
            self.tr("Unknown28"): "unk28",  # 未知28 / 未知28
            self.tr("Unknown29"): "unk29",  # 未知29 / 未知29
            self.tr("Unknown30"): "unk30",  # 未知30 / 未知30
            self.tr("Unknown31"): "unk31",  # 未知31 / 未知31
            self.tr("Unknown32"): "unk32",  # 未知32 / 未知32
            self.tr("Unknown33"): "unk33",  # 未知33 / 未知33
            self.tr("Unknown34"): "unk34",  # 未知34 / 未知34
            self.tr("Unknown35"): "unk35",  # 未知35 / 未知35
            self.tr("Unknown36"): "unk36",  # 未知36 / 未知36
            self.tr("Unknown37"): "unk37",  # 未知37 / 未知37
            self.tr("Unknown38"): "unk38",  # 未知38 / 未知38
            self.tr("Unknown39"): "unk39",  # 未知39 / 未知39
            self.tr("Unknown40"): "unk40",  # 未知40 / 未知40
            self.tr("Unknown41"): "unk41",  # 未知41 / 未知41
            self.tr("Unknown42"): "unk42",  # 未知42 / 未知42
            self.tr("Unknown43"): "unk43",  # 未知43 / 未知43
            self.tr("Unknown44"): "unk44",  # 未知44 / 未知44
            self.tr("Unknown45"): "unk45",  # 未知45 / 未知45
            self.tr("Unknown46"): "unk46",  # 未知46 / 未知46
            self.tr("Unknown47"): "unk47",  # 未知47 / 未知47
            self.tr("Unknown48"): "unk48",  # 未知48 / 未知48
            self.tr("Unknown49"): "unk49",  # 未知49 / 未知49
            self.tr("Unknown50"): "unk50",  # 未知50 / 未知50
        }
        return mapping

    # ========== 公开查询接口 ==========

    def get_field(self, display_name: str) -> str:
        """根据翻译后表头获取数据 key

        Args:
            display_name: 字段显示名（已通过 tr() 翻译）

        Returns:
            对应的数据 key

        Raises:
            KeyError: 未定义的字段名
        """
        if display_name in self._mapping:
            return self._mapping[display_name]
        raise KeyError(f"未定义名称[{display_name}]")

    def get_display(self, field_name: str) -> str:
        """根据数据 key 反向获取翻译后表头

        Args:
            field_name: 数据 key（如 "rname"）

        Returns:
            翻译后的表头文字

        Raises:
            KeyError: 未找到对应的显示名
        """
        reversed_mapping = {value: key for key, value in self._mapping.items()}
        if field_name in reversed_mapping:
            return reversed_mapping[field_name]
        raise KeyError(f"未找到字段[{field_name}]")

    def translateUI(self) -> None:
        """刷新映射表（语言切换后调用）

        语言变化时 self.tr() 的返回值改变，
        调用此方法重建 _mapping 以匹配新语言。
        """
        self.update_mapping()
