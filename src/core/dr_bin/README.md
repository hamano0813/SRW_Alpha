# DR.BIN 解析/构建模块

## 概述

`DR.BIN` 是《超级机器人大战α》ROM 中的机体图鉴数据文件，
由 449 个 LZSS 压缩块组成（1 个名册 + 448 条机体详情）。

## 文件结构

```code
0x0000~0x0707  指针表（450 × uint32 LE）
0x0708~EOF     数据区（LZSS 压缩块，pack=4 对齐）
```

- `ptr[0]` 指向块 0（名册），`ptr[449]` 指向文件尾
- 数据块数 = `ptr_count - 1` = 449 个

## 块 0：机体名册

- 448 × 0x30 字节记录
- 每条记录：左对齐文本 + `00` 截断 + `CD` 补齐

## 块 1~448：机体详情

解压后按固定偏移布局：

| 偏移    | 大小 | 字段     | 说明                        |
| ------- | ---- | -------- | --------------------------- |
| 0x00    | 0x30 | name     | 机体名，CD 掩码覆写         |
| 0x30    | 0x20 | height   | 全高（例: "20.8m"）         |
| 0x50    | 0x20 | weight   | 重量（例: "52.0t"）         |
| 0x70    | 0x40 | appr     | 出身作品，CD 掩码覆写       |
| 0xB0    | 4    | flags    | 4 字节标识                  |
| 0xB4+   | 可变 | desc     | 描述文本，48 字节对齐       |

所有文本字段左对齐、`00` 截断、`CD` 补齐。

### 描述文本格式

描述文本以 `00 00` 作为行分隔符，文本末尾固定有 `00 00`
尾随标记，最后以 `CD` 填充对齐到 48 的整数倍。

## Python API

### `parse(data, extra=None, trans=None) -> dict`

```python
from core.dr_bin import parse

data = parse(open("DR.BIN", "rb").read())
# {
#     "name": "dr",
#     "count": 448,
#     "roster": ["ヒュッケバインMK-II", ...],
#     "dr": [
#         {
#             "name": "ヒュッケバインMK-II",
#             "height": "20.8m",
#             "weight": "52.0t",
#             "appr": "オリジナル",
#             "flags": 21,
#             "desc": "月のマオ・インダストリーの協力を得て、...\n...",
#         }
#     ]
# }
```

### `build(data, extra=None, trans=None) -> bytearray`

```python
from core.dr_bin import build

raw = build(data)                                    # 往返重建
raw = build(data, extra=HALF_TEXT_EXTRA)             # 带映射重建
```

## 标识 (flags)

位于偏移 0xB0，4 字节 LE 整数。

## 构建

```bash
# 项目根目录统一构建
python build_project.py

# 或手动编译
cd src/core/dr_bin
python setup.py build_ext --inplace
```

## 依赖

- Python ≥ 3.12
- CPython 开发头文件
- LZSS 模块（`../lzss/lzss.c`）
- Codec 模块（`../codec/codec.c`）
