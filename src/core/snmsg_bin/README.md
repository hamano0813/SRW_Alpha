# SNMSG.BIN 解析/构建模块

## 概述

本模块提供 `SNMSG.BIN` 文件的解析与构建功能。
`SNMSG.BIN` 是《超级机器人大战α》ROM 中的消息文本数据文件，
**不含 LZSS 压缩**，无文件头，每条消息为固定 0x100 字节的 Shift-JIS 编码文本，
非文本部分全部为 `0x00` 填充。无掩码残影。

## 数据结构

### 文件结构

```
[0x0000] char text[0x100]   # 第 0 条消息（Shift-JIS x0213，00 填充）
[0x0100] char text[0x100]   # 第 1 条消息
...
[0xNNN0] char text[0x100]   # 第 N 条消息
```

总条数由文件大小决定：`count = size / 0x100`

### 字段说明

| 字段 | 偏移 | 大小 | 说明 |
|------|------|------|------|
| text | 0x00 | 0x100 | Shift-JIS x0213 编码文本，00 截断 |

## 实现架构

```table
┌─────────────────────────────────────────────────────────────┐
│  第一层（无压缩，直接 memcpy）                                  │
│  parse / build 内联 memcpy                                   │
│  原始 SNMSG.BIN ↔ 中间态 0x100 字节文本数组                    │
├─────────────────────────────────────────────────────────────┤
│  codec 子模块（独立编译链接）                                  │
│  codec_decode() — shift_jisx0213 → str + extra/trans        │
│  codec_encode() — str + extra/trans → shift_jisx0213 bytes  │
└─────────────────────────────────────────────────────────────┘
```

## Python API

### `parse(data, extra=None, trans=None) -> dict`

解析 SNMSG.BIN 数据。每条消息经 codec 解码为 `str`。

```python
from core.codec.extra import SNMSG_TEXT_EXTRA
from core.snmsg_bin import parse

data = parse(open("SNMSG.BIN", "rb").read(), extra=SNMSG_TEXT_EXTRA)
# data["snmsgs"][0] → {"snmsg": "ｼｭｳｶﾞﾝｾﾞﾝﾄﾓﾀﾞﾁ..."}  (dict)
```

返回结构：

```python
{
    "name": "snmsg",
    "count": 32544,
    "snmsgs": [
        {"snmsg": "ｼｭｳｶﾞﾝｾﾞﾝﾄﾓﾀﾞﾁ..."},     # 第 0 条消息
        {"snmsg": "ﾑｶｼ､ﾊﾙｶﾅﾙｷﾞﾝｶﾞ..."},       # 第 1 条消息
        ...
    ]
}
```

### `build(data, extra=None, trans=None) -> bytearray`

将 Python dict 重建为 SNMSG.BIN 二进制数据。

- snmsgs 中的项为 `dict`（`{"snmsg": str}`） → 经 `codec.encode()` 编码，超出 0x100 截断，不足 00 填充
- snmsgs 中的项为 `dict`（`{"snmsg": bytes}`）→ 直接写入，超出 0x100 截断，不足 00 填充

```python
from core.snmsg_bin import build

raw = build(data)                              # 往返重建
raw = build(data, extra=SNMSG_TEXT_EXTRA)      # 带映射重建
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
cd src/core/snmsg_bin
python setup.py build_ext --inplace
```

## 依赖

- Python ≥ 3.12
- CPython 开发头文件
- [Codec 模块](../codec/README.md)（子模块模式 `#include "codec/codec.h"`）

## 文本中的非常见字符

原始文件中出现的非 CJK/非 kana 特殊字符，留痕备查（可能涉及 extra 映射或字体需求）：

| 字符 | 码位 | 说明 |
|------|------|------|
| `α` | U+03B1 | 希腊字母 alpha（例：α波） |
| `β` | U+03B2 | 希腊字母 beta（例：グシオスβⅢ） |
| `ν` | U+03BD | 希腊字母 nu（例：νガンダム，`SNMSG_TEXT_EXTRA` 已有 `ﾙﾟ→ν`） |
| `σ` | U+03C3 | 希腊字母 sigma（例：何だとσ） |
| `…` | U+2026 | 水平省略号（24183 次，贯穿全文） |
| `Ⅱ` | U+2161 | 罗马数字 2（例：リック・ドムⅡ） |
| `Ⅲ` | U+2162 | 罗马数字 3（例：βⅢ） |
| `Ⅴ` | U+2164 | 罗马数字 5（例：ボルテスⅤ） |
| `−` | U+2212 | 减号/长横（例：ＳＤＦ−１） |
| `○` | U+25CB | 白色圆圈（例：デ○ラー機雷，伏字/消音） |
| `・` | U+30FB | 片假名中点（1074 次，列表分隔用）
