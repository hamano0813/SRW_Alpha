# PILOT.BIN 解析/构建模块

## 概述

本模块提供 `PILOT.BIN` 文件的解析与构建功能。
`PILOT.BIN` 是《超级机器人大战α》ROM 中的驾驶员数据文件，
**不含 LZSS 压缩**，结构为 flat 二进制。

二进制布局使用 **packed struct + bitfield** 定义，字段访问直观且与偏移表一一对应。

## 数据结构

### 文件结构

```cmd
[0x00] uint32 LE count           # 驾驶员总数
[0x04] PILOT[count]              # 连续排列的 PILOT 条目（无压缩）
```

### PILOT 结构体（0x70 字节）

```c
#pragma pack(1)
typedef struct {
    uint16_t code;               /* 0x00 代码 */
    uint16_t series : 10;        /* 0x02 换乘系（低 10 位） */
    uint16_t unknown1 : 6;       /* 0x02 高 6 位 */
    char     fname[37];          /* 0x04 全名（固定长度文本，掩码残影写入） */
    char     nname[13];          /* 0x29 机师名（固定长度文本，掩码残影写入） */
    uint8_t  cqb;                /* 0x36 格闘 */
    uint8_t  rng;                /* 0x37 射撃 */
    uint8_t  evd;                /* 0x38 回避 */
    uint8_t  hit;                /* 0x39 命中 */
    uint8_t  rxn;                /* 0x3A 反応 */
    uint8_t  skl;                /* 0x3B 技量 */
    uint8_t  spi[6];             /* 0x3C 精神列表 */
    uint8_t  spl[6];             /* 0x42 习得等级 */
    SKILL    sklu[3];            /* 0x48 成长型技能（3 条 × 0x0A） */
    uint8_t  sp;                 /* 0x66 ＳＰ */
    uint8_t  daction;            /* 0x67 ２回行动 */
    uint16_t skls;               /* 0x68 特殊技能（位域） */
    uint8_t  nature;             /* 0x6A 性格 */
    uint8_t  fsg;                /* 0x6B 气力组 */
    uint8_t  air;                /* 0x6C 空适应 */
    uint8_t  grd;                /* 0x6D 陆适应 */
    uint8_t  wtr;                /* 0x6E 海适应 */
    uint8_t  spc;                /* 0x6F 宇适应 */
} PILOT;
#pragma pack()
```

### SKILL 结构体（0x0A 字节）

```c
#pragma pack(1)
typedef struct {
    uint8_t sname;       /* 技能映射码 */
    uint8_t l1;          /* Lv1 效果等级 */
    uint8_t l2;
    uint8_t l3;
    uint8_t l4;
    uint8_t l5;
    uint8_t l6;
    uint8_t l7;
    uint8_t l8;
    uint8_t l9;
} SKILL;
#pragma pack()
```

## 实现架构

```table
┌─────────────────────────────────────────────────────────────┐
│  第一层（无压缩，直接 memcpy）                                  │
│  pilots_parse() / build 内联 memcpy                          │
│  原始 PILOT.BIN ↔ 中间态 PILOT 结构体数组                     │
├─────────────────────────────────────────────────────────────┤
│  第二层（字段映射）                                          │
│  struct PILOT / struct SKILL 直访字段和 bitfield              │
│  codec.h 内部 API                                            │
│  mask_overlay() -- 固定长度文本的掩码残影写入                  │
├─────────────────────────────────────────────────────────────┤
│  codec 子模块（独立编译链接）                                  │
│  codec_decode() — shift_jisx0213 → str + extra/trans        │
│  codec_encode() — str + extra/trans → shift_jisx0213 bytes  │
└─────────────────────────────────────────────────────────────┘
```

## 掩码残影

游戏初始化固定长度文本缓冲区时使用**默认掩码**，写入文本后整个缓冲区的内容
作为下一条驾驶员同字段的掩码。此残影效果在 `parse()` → `build()` 往返中完整保留。

### fname 默认掩码（37 字节）

前 10 字节因被第 0 条文本覆盖而不可考，假定为 `0x00`：

```hex
00 00 00 00 00 00 00 00 00 00  67 00 58 A5 F7 BF 00 00 67 00
40 00 00 00 00 00 00 00 00 08  00 00 00 08 00 00 BE
```

### nname 默认掩码（13 字节）

前 7 字节不可考，假定为 `0x00`：

```hex
00 00 00 00 00 00 00  22 8F F8 BF 00 00
```

## Python API

### `parse(data, extra=None, trans=None) -> dict`

解析 PILOT.BIN 数据。fname/nname 经 codec 解码为 `str`。

```python
from core.pilot_bin import parse

data = parse(open("PILOT.BIN", "rb").read())
# data["pilots"][0]["fname"] → "ｼｭｳ=ﾊｸﾊ"  (str)

# 带 extra/trans 映射
data = parse(raw, extra=HALF_TEXT_EXTRA, trans=my_trans)
```

返回结构：

```python
{
    "name": "pilot",
    "count": 469,
    "pilots": [
        {
            "fname": "ｼｭｳ=ﾊｸﾊ",          # str（已解码）
            "nname": "ｼｭｳ=ﾊｸﾊ",
            "code": 0,
            "series": 1,
            "unknown1": 0,
            "cqb": 122, "rng": 139, "evd": 163,
            "hit": 168, "rxn": 158, "skl": 168,
            "sp": 70, "daction": 62,
            "skls": 4,                     # uint16 位域
            "nature": 2, "fsg": 0,
            "air": 4, "grd": 4, "wtr": 2, "spc": 4,
            "spi": [18, 9, 20, 0, 19, 14],    # 精神列表（6 个）
            "spl": [1, 8, 23, 30, 39, 55],    # 习得等级（6 个）
            "sklu": [                          # 成长型技能（3 条）
                {"sname": 4, "l1": 1, "l2": 1, ..., "l9": 36},
                {"sname": 5, "l1": 1, "l2": 19, ..., "l9": 74},
                {"sname": 255, "l1": 255, ...}  # 255 = 空槽
            ]
        },
        ...
    ]
}
```

### `build(data, extra=None, trans=None) -> bytearray`

将 Python dict 重建为 PILOT.BIN 二进制数据。

- fname/nname 为 `str` → 经 `codec.encode()` 编码 + 掩码残影写入
- fname/nname 为 `bytes` → 向后兼容，直接覆写到掩码
- 空字符串 → 输出全 `00`，掩码残影重置

```python
from core.pilot_bin import build

raw = build(data)                      # 往返重建
raw = build(data, extra=HALF_TEXT_EXTRA)  # 带映射重建
```

### 文本字段类型

| 版本             | parse 返回 | build 接受              |
| ---------------- | ---------- | ----------------------- |
| 旧版（无 codec） | `bytes`    | `bytes`                 |
| 新版（有 codec） | `str`      | `str`（推荐）或 `bytes` |

## 构建

```bash
# 项目根目录统一构建（推荐）
python build_project.py

# 或手动编译
cd src/core/pilot_bin
python setup.py build_ext --inplace
```

## 依赖

- Python ≥ 3.12
- CPython 开发头文件
- [Codec 模块](../codec/README.md)（子模块模式 `#include "codec/codec.h"`）
