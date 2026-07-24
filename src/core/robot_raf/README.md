# ROBOT.RAF 解析/构建模块

## 概述

本模块提供 `ROBOT.RAF` 文件的解析与构建功能。
`ROBOT.RAF` 是《超级机器人大战α》ROM 中的机体数据文件，
使用 LZSS 压缩，包含机体（ROBOT）与武器（WEAPON）的数据。

二进制布局使用 **packed struct + bitfield** 定义，字段访问直观且与偏移表一一对应。

## 数据结构

### 文件结构

- 文件由两部分组成：头部和数据部
- 头部：4 字节记录数 N + N × 4 字节指针表
- 数据部：N 个 LZSS 压缩块
  - 每个块：4 字节解压后大小 + 4 字节保留 (0x00) + LZSS 压缩流
  - 指针指向块相对数据部起始的偏移量

### ROBOT 结构体（0x2C4 字节）

```c
#pragma pack(1)
typedef struct {
    char     rname[26];          // 机体名（固定长度文本，掩码残影写入）
    uint16_t code;               // 代码
    uint8_t  type : 4;           // 移动类型
    uint8_t  unknown1 : 4;
    uint8_t  move;               // 移动力
    uint16_t hp;
    uint16_t en;
    uint16_t mobility;           // 运动性
    uint16_t armor;              // 装甲
    uint16_t limit;              // 限界
    uint8_t  size;               // 体积
    uint8_t  slot;               // 芯片数
    uint16_t series : 10;        // 换乘系
    uint16_t unknown2 : 6;
    uint32_t abi : 31;           // 特性
    uint32_t unknown3 : 1;
    uint16_t rep;                // 修理费
    uint16_t cost;               // 资金
    uint8_t  tgrp;               // 变形组号
    uint8_t  tsn;                // 变形序号
    uint8_t  cgrp;               // 合体组号
    uint8_t  csn;                // 合体序号
    uint16_t core;               // 核心机体
    uint8_t  count;              // 合体数
    uint8_t  option;             // 换装系统
    uint8_t  bgm;                // 机体BGM
    uint8_t  unknown4;
    uint8_t  rcls : 1;           // bit0 单位类别：0=超级系, 1=真实系
    uint8_t  uval : 2;           // bits1-2 单位价值：0=普通, 1=中等, 2=高
    uint8_t  unknown5 : 5;       // bits3-7 原剩余位
    uint8_t  u6_flag : 1;        // bit0 用途不明
    uint8_t  tech : 2;           // bits1-2 科技分类：0=超科技, 1=工程学, 2=灵力
    uint8_t  unknown6 : 5;       // bits3-7 剩余位
    uint8_t  air;                // 空适应
    uint8_t  grd;                // 陆适应
    uint8_t  wtr;                // 海适应
    uint8_t  spc;                // 宇适应
    WEAPON   weapons[16];        // 武器列表
} ROBOT;
#pragma pack()
```

### WEAPON 结构体（0x28 字节）

```c
#pragma pack(1)
typedef struct {
    uint8_t  code : 4;
    uint8_t  newtype : 2;
    uint8_t  aura : 2;
    uint8_t  morale;
    uint8_t  custom : 2;
    uint8_t  rngs : 2;
    uint8_t  rngl : 4;
    uint8_t  mcls : 2;
    uint8_t  radius : 3;
    uint8_t  unknown1 : 3;
    uint16_t damage;
    uint8_t  wclass : 1;
    uint8_t  attr : 7;
    uint8_t  unknown2 : 4;
    uint8_t  bonus : 4;
    char     wname[21];          // 武器名（固定长度文本，掩码残影写入）
    uint8_t  mrng;               // 地图武器射程
    uint8_t  mshow;              // 地图武器演出
    uint8_t  encost;             // EN 消耗
    int8_t   hitrate;            // 命中
    int8_t   crt;                // CT
    uint8_t  ammod;              // 初始弹数
    uint8_t  ammom;              // 最大弹数
    uint8_t  air;
    uint8_t  grd;
    uint8_t  wtr;
    uint8_t  spc;
} WEAPON;
#pragma pack()
```

## 实现架构

```table
┌─────────────────────────────────────────────────────────────┐
│  第一层（LZSS）                                              │
│  _entries_decompress() / _entries_compress()                 │
│  原始 RAF 文件 ↔ 解压后的连续条目缓冲区                       │
├─────────────────────────────────────────────────────────────┤
│  第二层（字段映射）                                          │
│  struct ROBOT / struct WEAPON 直访字段和 bitfield            │
│  codec.h 内部 API                                            │
├─────────────────────────────────────────────────────────────┤
│  codec 子模块（独立编译链接）                                  │
│  codec_decode() — shift_jisx0213 → str + extra/trans        │
│  codec_encode() — str + extra/trans → shift_jisx0213 bytes  │
└─────────────────────────────────────────────────────────────┘
```

## 掩码残影

游戏初始化固定长度文本缓冲区时使用**默认掩码**，写入文本后整个缓冲区的内容
作为下一台机体同字段的掩码。此残影效果在 `parse()` → `build()` 往返中完整保留。

### rname 默认掩码（26 字节）

```hex
20 20 20 20 20 20 20 20 20 20 20 20 A0 A1 A2 A3 A4 A5 A6 A7 A8 A9 AA AB AC AD
```

### wname 默认掩码（每个武器槽位 21 字节）

| 槽位    | 掩码值                                        |
| ------- | --------------------------------------------- |
| W00     | `20` × 21                                     |
| W01     | `08 09 0A ... 1A 1B 1C`（08~1C）              |
| W02     | `30 31 ... 40 61 62 63 64`（跳过 0x41~0x60）  |
| W03     | `58 59 ... 6A 6B 6C`（58~6C）                 |
| W04     | `20` × 21                                     |
| W05     | `A8 A9 ... BA BB BC`（A8~BC）                 |
| W06     | `D0 D1 ... DF 20 20 20 20 20`（D0~DF → 20×5） |
| W07~W15 | `00` × 21（空武器槽）                         |

## Python API

### `parse(data, extra=None, trans=None) -> dict`

解析 ROBOT.RAF 数据。rname/wname 经 codec 解码为 `str`。

```python
from core.robot_raf import parse

data = parse(open("ROBOT.RAF", "rb").read())
# data["robots"][0]["rname"] → "ｶﾞﾝﾀﾞﾑ"  (str)

# 带 extra/trans 映射
data = parse(raw, extra=HALF_TEXT_EXTRA, trans=my_trans)
```

返回结构：

```python
{
    "name": "robot",
    "count": 486,
    "robots": [
        {
            "rname": "ｶﾞﾝﾀﾞﾑ",       # str（已解码）
            "code": 0,
            "type": 1,
            "rcls": 1,               # bit0 单位类别：0=超级系, 1=真实系
            "uval": 0,               # bits1-2 单位价值：0=普通, 1=中等, 2=高
            "unknown5": 0,           # bits3-7 原 unknown5 高 5 位
            "u6_flag": 0,            # bit0 用途不明
            "tech": 1,               # bits1-2 科技分类：0=超科技, 1=工程学, 2=灵力
            "weapons": [
                {"wname": "ﾊﾞﾙｶﾝ", "damage": 800, ...},
                ...
            ]
        },
        ...
    ]
}
```

### `build(data, extra=None, trans=None) -> bytearray`

将 Python dict 重建为 ROBOT.RAF 二进制数据。

- rname/wname 为 `str` → 经 `codec.encode()` 编码 + 掩码残影写入
- rname/wname 为 `bytes` → 向后兼容，直接覆写到掩码
- 空字符串 → 输出全 `00`，掩码残影重置

```python
from core.robot_raf import build

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
cd src/core/robot_raf
python setup.py build_ext --inplace
```

## 依赖

- Python ≥ 3.12
- CPython 开发头文件
- [LZSS 模块](../lzss/README.md)（编译时静态链接 `lzss.c`）
- [Codec 模块](../codec/README.md)（子模块模式 `#include "codec/codec.h"`）
