# ROBOT.RAF 解析/构建模块

## 概述

本模块提供 `ROBOT.RAF` 文件的解析与构建功能。
`ROBOT.RAF` 是《超级机器人大战α》ROM 中的机体数据文件，
使用 LZSS 压缩，包含机体（ROBOT）与武器（WEAPON）的数据。

## 数据结构

### 文件结构

- 文件由两部分组成：头部和数据部
- 头部：4 字节记录数 N + N × 4 字节指针表
- 数据部：N 个数据块
  - 每个数据块：4 字节解压后大小 + 4 字节保留 (0x00) + LZSS 压缩流
  - 指针指向数据块相对数据部起始的偏移量

### ROBOT 数据块

解压后定长 `0x2C4` 字节，包含：

| 偏移 | 大小        | 类型       | 字段     | 说明     |
| ---- | ----------- | ---------- | -------- | -------- |
| 0x00 | 0x1A        | char[26]   | rname    | 机体     |
| 0x1A | 2           | UINT16     | code     | 代码     |
| 0x1C | bitfield:4  |            | type     | 移动类型 |
| 0x1C | bitfield:4  |            | unknown1 | *保留*   |
| 0x1D | 1           | UINT8      | move     | 移动力   |
| 0x1E | 2           | UINT16     | hp       | HP       |
| 0x20 | 2           | UINT16     | en       | EN       |
| 0x22 | 2           | UINT16     | mobility | 运动性   |
| 0x24 | 2           | UINT16     | armor    | 装甲     |
| 0x26 | 2           | UINT16     | limit    | 限界     |
| 0x28 | 1           | UINT8      | size     | 体积     |
| 0x29 | 1           | UINT8      | slot     | 芯片     |
| 0x2A | bitfield:10 |            | series   | 换乘系   |
| 0x2A | bitfield:6  |            | unknown2 | *保留*   |
| 0x2C | bitfield:31 |            | abi      | 特性     |
| 0x2C | bitfield:1  |            | unknown3 | *保留*   |
| 0x30 | 2           | UINT16     | rep      | 修理费   |
| 0x32 | 2           | UINT16     | cost     | 资金     |
| 0x34 | 1           | UINT8      | tgrp     | 变形组号 |
| 0x35 | 1           | UINT8      | tsn      | 变形序号 |
| 0x36 | 1           | UINT8      | cgrp     | 合体组号 |
| 0x37 | 1           | UINT8      | csn      | 合体序号 |
| 0x38 | 2           | UINT16     | core     | 核心机体 |
| 0x3A | 1           | UINT8      | count    | 合体数   |
| 0x3B | 1           | UINT8      | option   | 换装系统 |
| 0x3C | 1           | UINT8      | bgm      | 机体BGM  |
| 0x3D | 1           | UINT8      | unknown4 | *保留*   |
| 0x3E | 1           | UINT8      | unknown5 | *保留*   |
| 0x3F | 1           | UINT8      | unknown6 | *保留*   |
| 0x40 | 1           | UINT8      | air      | 空适应   |
| 0x41 | 1           | UINT8      | grd      | 陆适应   |
| 0x42 | 1           | UINT8      | wtr      | 海适应   |
| 0x43 | 1           | UINT8      | spc      | 宇适应   |
| 0x44 | 0x280       | WEAPON[16] | weapons  | 武器列表 |

### WEAPON 数据块

定长 `0x28` 字节，包含：

| 偏移 | 大小       | 类型     | 字段     | 说明                 |
| ---- | ---------- | -------- | -------- | -------------------- |
| 0x00 | bitfield:4 |          | code     | 代码                 |
| 0x00 | bitfield:2 |          | newtype  | 新人类               |
| 0x00 | bitfield:2 |          | aura     | 圣战士               |
| 0x01 | 1          | UINT8    | morale   | 气力                 |
| 0x02 | bitfield:2 |          | custom   | 改造类型             |
| 0x02 | bitfield:2 |          | rngs     | 近射程               |
| 0x02 | bitfield:4 |          | rngl     | 远射程               |
| 0x03 | bitfield:2 |          | mcls     | 地图武器分类         |
| 0x03 | bitfield:3 |          | radius   | 着弹点指定型攻击半径 |
| 0x03 | bitfield:3 |          | unknown1 | *保留*               |
| 0x04 | 2          | UINT16   | damage   | 攻击力               |
| 0x06 | bitfield:1 |          | class    | 分类                 |
| 0x06 | bitfield:7 |          | attr     | 属性                 |
| 0x07 | bitfield:4 |          | unknown2 | *保留*               |
| 0x07 | bitfield:4 |          | bonus    | 改造追加             |
| 0x08 | 0x15       | char[21] | wname    | 武器                 |
| 0x1D | 1          | UINT8    | mrng     | 地图武器射程         |
| 0x1E | 1          | UINT8    | mshow    | 地图武器演出         |
| 0x1F | 1          | UINT8    | encost   | EN                   |
| 0x20 | 1          | INT8     | hitrate  | 命中                 |
| 0x21 | 1          | INT8     | crt      | CT                   |
| 0x22 | 1          | UINT8    | ammod    | 初始弹数             |
| 0x23 | 1          | UINT8    | ammom    | 最大弹数             |
| 0x24 | 1          | UINT8    | air      | 空适应               |
| 0x25 | 1          | UINT8    | grd      | 陆适应               |
| 0x26 | 1          | UINT8    | wtr      | 海适应               |
| 0x27 | 1          | UINT8    | spc      | 宇适应               |

## Python API

### `parse(data: bytes | bytearray) -> dict`

解析 ROBOT.RAF 数据，返回 Python dict：

```python
{
    "name": "robot",
    "count": 486,
    "robots": [
        {
            "rname": b"\\x00..."         # 原始字节（后续接入 codec 后改为 str）
            "code": 0,
            "type": 1,
            ...
            "weapons": [
                {"code": 0, "damage": 2800, ...},
                ...
            ]
        },
        ...
    ]
}
```

### `build(data: dict) -> bytearray`

将 Python dict 重建为 ROBOT.RAF 二进制数据。输入格式与 `parse()` 返回一致。

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
- LZSS 模块（`src/core/lzss/lzss.c`，编译时静态链接）
