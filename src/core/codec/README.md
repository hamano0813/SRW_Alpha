# 文本编解码模块 (codec)

## 概述

本模块提供《超级机器人大战α》ROM 文件中使用的 Shift-JIS x0213 编码文本的
解码与编码功能。

游戏中的文本分为两类：

- **定长文本**：存储在固定大小的缓冲区中（如 `char[26]`），缓冲区有特定模式的
  掩码填充。文本以 `0x00` 终结，之后的掩码字节不参与解码。
- **不定长文本**：仅存储文本本身，文本长度（含 `0x00`）在外部记录。

游戏中部分字符使用了冷僻字码位或特殊控制码，需通过 **extra 映射表**替换为
标准 Unicode 文本。用户还可通过 **trans 映射表**自定义文本替换（如汉化修正）。

## 架构

```cmd
┌─────────────────────────────────────────────────────┐
│                Python 层（__init__.py）             │
│  纯 re-export: from ._codec import decode/encode    │
├─────────────────────────────────────────────────────┤
│                C 扩展层（_codec.pyd）               │
│  decode() / encode() / encode_var()                 │
│  Shift-JIS x0213 转换 + 扫描式文本替换              │
├─────────────────────────────────────────────────────┤
│          C 内部 API（codec_decode / codec_encode）  │
│           供 robot_raf.c 等子模块链接调用           │
└─────────────────────────────────────────────────────┘
```

## API

### `decode(data, extra=None, trans=None) -> str`

将 Shift-JIS x0213 字节解码为文本。

| 参数    | 类型                    | 默认值 | 说明                           |
| ------- | ----------------------- | ------ | ------------------------------ |
| `data`  | `bytes \| bytearray`    | —      | 输入字节数据，读到 `0x00` 截断 |
| `extra` | `dict[str,str] \| None` | `None` | 游戏内码 → 显示文本映射        |
| `trans` | `dict[str,str] \| None` | `None` | 用户自定义文本替换             |

处理顺序：`0x00 截断 → shift_jisx0213 解码 → extra → trans`

```python
from core.codec import decode

raw = robot_data[0:0x1A]
name = decode(raw, extra=HALF_TEXT_EXTRA)
```

### `encode(text, mask, extra=None, trans=None) -> bytearray`

定长文本编码。在 mask 副本上覆写 Shift-JIS 编码 + `0x00` 终结。

| 参数    | 类型                    | 默认值 | 说明                       |
| ------- | ----------------------- | ------ | -------------------------- |
| `text`  | `str`                   | —      | 要编码的文本               |
| `mask`  | `bytes \| bytearray`    | —      | 完整缓冲区内容（长度 ≥ 2） |
| `extra` | `dict[str,str] \| None` | `None` | 映射表                     |
| `trans` | `dict[str,str] \| None` | `None` | 用户自定义替换             |

处理顺序：`trans_rev → extra_rev → shift_jisx0213 编码 → 覆写到 mask`

```python
from core.codec import encode

mask = bytearray([0xF4] * 26)
buf = encode("νガンダム", mask, extra=HALF_TEXT_EXTRA)
```

### `encode_var(text, extra=None, trans=None) -> (bytes, int)`

不定长文本编码。返回 `(含 0x00 终结的字节, 总长度)`。

```python
from core.codec import encode_var

data, length = encode_var("テスト", extra=HALF_TEXT_EXTRA)
# data = b'\x83\x65\x83\x58\x83\x67\x00', length = 7
```

### 映射替换策略

扫描式替换从左到右逐字符匹配，优先匹配最长键，匹配完成后跳过已匹配区域，
不再重复处理替换后的文本。

```python
extra = {
    'ﾔﾟﾕﾟ': 'MK-',   # 4 个半角片假名 → "MK-"
    '-': 'ー',         # 半角连字符 → 全角长音
}
# 输入 'ﾔﾟﾕﾟ' → 匹配 4 字符的键 → 输出 "MK-" (短横不被二次替换)
```

## 文件说明

| 文件          | 说明                                                      |
| ------------- | --------------------------------------------------------- |
| `codec.c`     | C 扩展源代码，实现 `_codec` 模块                          |
| `codec.h`     | C 内部 API 头文件（`codec_decode` / `codec_encode` 声明） |
| `codec.pyi`   | C 扩展类型存根                                            |
| `__init__.py` | Python 包装层（re-export C 模块函数）                     |
| `setup.py`    | setuptools 构建配置                                       |
| `setup.cfg`   | 编译器配置（mingw32）                                     |
| `README.md`   | 本文件                                                    |

## 子模块模式

`codec.c` 支持两种编译模式：

- **独立模块**（默认）：编译为 `_codec.pyd`，通过 `from core.codec import decode` 调用
- **子模块模式**：定义 `CODEC_AS_SUBMODULE` 宏后 `#include` 到其他 C 扩展中，
  跳过 `PyInit__codec`，直接链接 `codec_decode()` / `codec_encode()` 函数。

子模块模式下，通过 `codec.h` 头文件声明内部 API，`codec.c` 作为独立编译单元
链接到宿主模块（如 `robot_raf.c`）。构建时需要：

1. 在 `.c` 文件中包含头文件：`#include "codec/codec.h"`（通过 `include_dirs` 解析）
2. 在 `setup.py` 中将 `codec.c` 加入源列表并定义 `CODEC_AS_SUBMODULE`

当前 `robot_raf.c` 使用此模式：

```c
/* robot_raf.c */
#include "codec/codec.h"   /* include_dirs=[".."] → src/core/codec/codec.h */
```

```python
# setup.py
Extension("_robot_raf",
    sources=["robot_raf.c", "../codec/codec.c"],
    define_macros=[("CODEC_AS_SUBMODULE", None)])
```

这样 `robot_raf` 可直接调用 `codec_decode()` / `codec_encode()`，
无需运行时 Python import。

## 构建

```bash
# 项目根目录统一构建（推荐）
python build_project.py

# 或手动编译
cd src/core/codec
python setup.py build_ext --inplace
```

## 数据流

```cmd
解码: 字节 → 0x00截断 → shift_jisx0213 → extra → trans → str
编码: str → trans_rev → extra_rev → shift_jisx0213 → 覆写/输出
```

## 依赖

- Python ≥ 3.12（内置 `shift_jisx0213` 编解码器）
- CPython 开发头文件
