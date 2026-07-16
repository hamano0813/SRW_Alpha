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
            self.tr("robot name"): "rname",  # 机体 / ユニット
            self.tr("code"): "code",  # 编码 / コード
            self.tr("movement type"): "type",  # 移动类型 / 移動タイプ
            self.tr("movement"): "move",  # 移动力 / 移動力
            self.tr("hit points"): "hp",  # HP / HP
            self.tr("energy"): "en",  # EN / EN
            self.tr("mobility"): "mobility",  # 运动性 / 運動性
            self.tr("armor"): "armor",  # 装甲 / 装甲
            self.tr("limit"): "limit",  # 限界 / 限界
            self.tr("size"): "size",  # 体积 / サイズ
            self.tr("parts slot"): "slot",  # 零件插槽 / パーツスロット
            self.tr("series"): "series",  # 换乘系 / のりかえ系
            self.tr("abilities"): "abi",  # 特殊能力 / 特殊能力
            self.tr("repair cost"): "rep",  # 修理费 / 修理費
            self.tr("cost"): "cost",  # 资金 / 資金
            self.tr("transform group number"): "tgrp",  # 变形组号 / 変形グループ
            self.tr("transform sequence number"): "tsn",  # 变形序号 / 変形シーケンス
            self.tr("combine group number"): "cgrp",  # 合体组号 / 合体グループ
            self.tr("combine sequence number"): "csn",  # 合体序号 / 合体シーケンス
            self.tr("core robot"): "core",  # 核心机体 / コアユニット
            self.tr("combine count"): "count",  # 合体数 / 合体数
            self.tr("option parts system"): "option",  # 机体换装 / ユニット換装
            self.tr("background music"): "bgm",  # BGM / BGM
            self.tr("air"): "air",  # 空 / 空
            self.tr("ground"): "grd",  # 陆 / 陸
            self.tr("water"): "wtr",  # 海 / 海
            self.tr("space"): "spc",  # 宇 / 宇
            self.tr("weapons"): "weapons",  # 武器列表 / 武器リスト
        }
        return mapping

    def _init_weapon(self):
        """ROBOT.RAF 武器数据结构字段"""
        mapping = {
            self.tr("code"): "code",  # 编码 / コード
            self.tr("required newtype level"): "newtype",  # 新人类等级 / ニュータイプレベル
            self.tr("required aura level"): "aura",  # 圣战士等级 / 聖戦士レベル
            self.tr("required morale value"): "morale",  # 必要气力 / 必要気力
            self.tr("custom type"): "custom",  # 改造类型 / 改造タイプ
            self.tr("short range"): "rngs",  # 近射程 / 近射程
            self.tr("long range"): "rngl",  # 远射程 / 遠射程
            self.tr("map weapon class"): "mcls",  # 地图武器分类 / マップ兵器分類
            self.tr("map weapon radius"): "radius",  # 着弹指定型半径 / 着弾指定型半径
            self.tr("damage"): "damage",  # 攻击力 / 攻撃力
            self.tr("weapon class"): "class",  # 武器分类 / 武器分類
            self.tr("attribute"): "attr",  # 属性 / 属性
            self.tr("custom bonus"): "bonus",  # 改造追加 / 改造ボーナス
            self.tr("weapon name"): "wname",  # 武器名 / 武器名
            self.tr("map weapon range"): "mrng",  # 方向指定型范围 / 方向指定型範囲
            self.tr("map weapon show"): "mshow",  # 地图武器演出 / マップ兵器演出
            self.tr("energy cost"): "encost",  # 消耗EN / 消費EN
            self.tr("accuracy"): "hit",  # 命中 / 命中
            self.tr("critical"): "crt",  # 会心补正 / クリティカル補正
            self.tr("default ammo"): "ammod",  # 初始弹药 / 初期弾数
            self.tr("maximum ammo"): "ammom",  # 最大弹药 / 最大弾数
            self.tr("air"): "air",  # 空 / 空
            self.tr("ground"): "grd",  # 陆 / 陸
            self.tr("water"): "wtr",  # 海 / 海
            self.tr("space"): "spc",  # 宇 / 宇
        }
        return mapping

    def _init_pilot(self):
        """PILOT.BIN 驾驶员数据结构字段"""
        mapping = {
            self.tr("code"): "code",  # 编码 / コード
            self.tr("series"): "series",  # 换乘系 / のりかえ系
            self.tr("fullname"): "fname",  # 全名 / 名前
            self.tr("nickname"): "nname",  # 机师 / パイロット
            self.tr("combat"): "cqb",  # 格斗 / 格闘
            self.tr("ranged"): "rng",  # 射击 / 射撃
            self.tr("evasion"): "evd",  # 回避 / 回避
            self.tr("accuracy"): "hit",  # 命中 / 命中
            self.tr("reaction"): "rxn",  # 反应 / 反応
            self.tr("skill"): "skl",  # 技量 / 技量
            self.tr("spirit commands"): "spi",  # 精神指令 / 精神コマンド
            self.tr("spirit level"): "spl",  # 习得等级 / 習得レベル
            self.tr("upgraded skills"): "sklu",  # 等级制技能 / レベル制技能
            self.tr("SP"): "sp",  # SP / SP
            self.tr("double action"): "daction",  # 2次行动 / 2回行動
            self.tr("special skills"): "skls",  # 特殊技能 / 特殊技能
            self.tr("nature"): "nature",  # 性格 / 性格
            self.tr("friendship group"): "fsg",  # 气力组 / 気力グループ
            self.tr("air"): "air",  # 空 / 空
            self.tr("ground"): "grd",  # 陆 / 陸
            self.tr("water"): "wtr",  # 海 / 海
            self.tr("space"): "spc",  # 宇 / 宇
        }
        return mapping

    def _init_skill(self):
        """PILOT.BIN 特殊技能数据结构字段"""
        mapping = {
            self.tr("skill name"): "sname",  # 技能 / スキル
            self.tr("skill level1"): "l1",  # Lv1 / Lv1
            self.tr("skill level2"): "l2",  # Lv2 / Lv2
            self.tr("skill level3"): "l3",  # Lv3 / Lv3
            self.tr("skill level4"): "l4",  # Lv4 / Lv4
            self.tr("skill level5"): "l5",  # Lv5 / Lv5
            self.tr("skill level6"): "l6",  # Lv6 / Lv6
            self.tr("skill level7"): "l7",  # Lv7 / Lv7
            self.tr("skill level8"): "l8",  # Lv8 / Lv8
            self.tr("skill level9"): "l9",  # Lv9 / Lv9
        }
        return mapping

    def _init_dc(self):
        """DC.BIN 人物图鉴数据结构字段"""
        mapping = {
            self.tr("full name"): "fname",  # 全名 / フルネーム
            self.tr("pet name"): "pname",  # 爱称 / 愛称
            self.tr("appearance"): "appr",  # 登场作品 / 登場作品
            self.tr("voice actor"): "voice",  # 声优 / 声優
            self.tr("flags"): "flags",  # 标志 / フラグ
            self.tr("description"): "desc",  # 事典 / 事典
        }
        return mapping

    def _init_dr(self):
        """DR.BIN 机体图鉴数据结构字段"""
        mapping = {
            self.tr("name"): "name",  # 名称 / 名称
            self.tr("height"): "height",  # 全长 / 全長
            self.tr("weight"): "weight",  # 重量 / 重量
            self.tr("appearance"): "appr",  # 登场作品 / 登場作品
            self.tr("flags"): "flags",  # 标志 / フラグ
            self.tr("description"): "desc",  # 介绍 / 紹介
        }
        return mapping

    def _init_sndata(self):
        """SNDATA.BIN 场景索引数据结构字段"""
        mapping = {
            self.tr("scenario pointer"): "sptr",  # 场景指针 / シナリオポインタ
            self.tr("scenario data"): "sndata",  # 场景数据 / シナリオデータ
        }
        return mapping

    def _init_scenario(self):
        """SNDATA.BIN 关卡指令块数据结构字段"""
        mapping = {
            self.tr("block count"): "bcount",  # 块数量 / ブロック数
            self.tr("block length"): "blen",  # 块长度 / ブロック長
            self.tr("block pointers"): "bptrs",  # 块指针 / ブロックポインタ
            self.tr("command data"): "cdata",  # 指令数据 / コマンドデータ
        }
        return mapping

    def _init_command(self):
        """SNDATA.BIN 单条指令数据结构字段"""
        mapping = {
            self.tr("command code"): "ccode",  # 指令代码 / コマンドコード
            self.tr("command count"): "ccount",  # 指令计数 / コマンド数
            self.tr("command params"): "cparams",  # 指令参数 / コマンドパラメータ
            self.tr("command explain"): "explain",  # 指令说明 / コマンド説明
        }
        return mapping

    def _init_snmsg(self):
        """SNMSG.BIN 消息数据结构字段"""
        mapping = {
            self.tr("message"): "msg",  # 剧情文本 / シナリオメッセージ
        }
        return mapping

    def _init_script(self):
        """SCRIPT.BIN 脚本文本数据结构字段"""
        mapping = {
            self.tr("script command"): "scmd",  # 剧本指令 / 脚本コマンド
            self.tr("script params1"): "sparams1",  # 剧本参数1 / 脚本パラメータ1
            self.tr("script params2"): "sparams2",  # 剧本参数2 / 脚本パラメータ2
            self.tr("script expand"): "sexpand",  # 扩展文本 / 拡張テキスト
        }
        return mapping

    def _init_aiunp(self):
        """AIUNP.BIN AI 数据结构字段"""
        mapping = {
            self.tr("ai pointers"): "aiptrs",  # AI 指针 / AIポインタ
            self.tr("ai data"): "aidata",  # AI 数据 / AIデータ
            self.tr("ai count"): "aicount",  # AI 数量 / AI数
            self.tr("ai length"): "ailen",  # AI 长度 / AI長
            self.tr("ai list"): "ailist",  # AI 列表 / AIリスト
            self.tr("AI"): "ai",  # AI / AI
            self.tr("valid"): "valid",  # 有效 / 有効
            self.tr("move round"): "mrnd",  # 开始移动回合 / 移動開始ラウンド
            self.tr("own move"): "omov",  # 自主移动 / 自主移動
            self.tr("own attack"): "oatk",  # 自主攻击 / 自主攻撃
            self.tr("target pilot"): "tpil",  # 目标驾驶员 / 目標パイロット
            self.tr("target x"): "tx",  # 目标X / 目標X
            self.tr("target y"): "ty",  # 目标Y / 目標Y
        }
        return mapping

    def _init_unknown(self):
        """未知数据结构字段（占位）"""
        mapping = {
            self.tr("unknown01"): "unk01",  # 未知01 / 未知01
            self.tr("unknown02"): "unk02",  # 未知02 / 未知02
            self.tr("unknown03"): "unk03",  # 未知03 / 未知03
            self.tr("unknown04"): "unk04",  # 未知04 / 未知04
            self.tr("unknown05"): "unk05",  # 未知05 / 未知05
            self.tr("unknown06"): "unk06",  # 未知06 / 未知06
            self.tr("unknown07"): "unk07",  # 未知07 / 未知07
            self.tr("unknown08"): "unk08",  # 未知08 / 未知08
            self.tr("unknown09"): "unk09",  # 未知09 / 未知09
            self.tr("unknown10"): "unk10",  # 未知10 / 未知10
            self.tr("unknown11"): "unk11",  # 未知11 / 未知11
            self.tr("unknown12"): "unk12",  # 未知12 / 未知12
            self.tr("unknown13"): "unk13",  # 未知13 / 未知13
            self.tr("unknown14"): "unk14",  # 未知14 / 未知14
            self.tr("unknown15"): "unk15",  # 未知15 / 未知15
            self.tr("unknown16"): "unk16",  # 未知16 / 未知16
            self.tr("unknown17"): "unk17",  # 未知17 / 未知17
            self.tr("unknown18"): "unk18",  # 未知18 / 未知18
            self.tr("unknown19"): "unk19",  # 未知19 / 未知19
            self.tr("unknown20"): "unk20",  # 未知20 / 未知20
            self.tr("unknown21"): "unk21",  # 未知21 / 未知21
            self.tr("unknown22"): "unk22",  # 未知22 / 未知22
            self.tr("unknown23"): "unk23",  # 未知23 / 未知23
            self.tr("unknown24"): "unk24",  # 未知24 / 未知24
            self.tr("unknown25"): "unk25",  # 未知25 / 未知25
            self.tr("unknown26"): "unk26",  # 未知26 / 未知26
            self.tr("unknown27"): "unk27",  # 未知27 / 未知27
            self.tr("unknown28"): "unk28",  # 未知28 / 未知28
            self.tr("unknown29"): "unk29",  # 未知29 / 未知29
            self.tr("unknown30"): "unk30",  # 未知30 / 未知30
            self.tr("unknown31"): "unk31",  # 未知31 / 未知31
            self.tr("unknown32"): "unk32",  # 未知32 / 未知32
            self.tr("unknown33"): "unk33",  # 未知33 / 未知33
            self.tr("unknown34"): "unk34",  # 未知34 / 未知34
            self.tr("unknown35"): "unk35",  # 未知35 / 未知35
            self.tr("unknown36"): "unk36",  # 未知36 / 未知36
            self.tr("unknown37"): "unk37",  # 未知37 / 未知37
            self.tr("unknown38"): "unk38",  # 未知38 / 未知38
            self.tr("unknown39"): "unk39",  # 未知39 / 未知39
            self.tr("unknown40"): "unk40",  # 未知40 / 未知40
            self.tr("unknown41"): "unk41",  # 未知41 / 未知41
            self.tr("unknown42"): "unk42",  # 未知42 / 未知42
            self.tr("unknown43"): "unk43",  # 未知43 / 未知43
            self.tr("unknown44"): "unk44",  # 未知44 / 未知44
            self.tr("unknown45"): "unk45",  # 未知45 / 未知45
            self.tr("unknown46"): "unk46",  # 未知46 / 未知46
            self.tr("unknown47"): "unk47",  # 未知47 / 未知47
            self.tr("unknown48"): "unk48",  # 未知48 / 未知48
            self.tr("unknown49"): "unk49",  # 未知49 / 未知49
            self.tr("unknown50"): "unk50",  # 未知50 / 未知50
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
