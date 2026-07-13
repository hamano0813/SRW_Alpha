# LZSS 压缩/解压模块

## 概述

本模块提供 LZSS 算法的压缩与解压功能，用于《超级机器人大战α》ROM 中的压缩数据块。

## 格式

```code
+----------------+
| raw_size  4byte |  解压后数据大小（小端序 uint32）
+----------------+
| reserved  4byte |  保留字段（全零）
+----------------+
| LZSS stream     |  压缩流
+----------------+
```

## 参数

| 参数         | 值                                  |
| ------------ | ----------------------------------- |
| 窗口大小     | 4096 字节                           |
| 匹配位置     | 12 bit                              |
| 匹配长度     | 4 bit                               |
| 存储长度范围 | 0 ~ 15                              |
| 实际长度范围 | 3 ~ 18（存储值 + THRESHOLD(2) + 1） |
| 初始零填充   | 4078 字节（模拟窗口初始状态）       |

## 算法

### 压缩

每 8 个 token 用一个标志字节（flag byte）描述：

- **标志位 = 1**：原始字节（literal），直接输出 1 字节
- **标志位 = 0**：匹配引用（match），输出 2 字节

匹配编码（2 字节）：

```code
byte0:  position low 8 bit
byte1:  [position high 4 bit | length 4 bit]
```

滑动窗口从初始零填充开始，搜索最长匹配（最多 18 字节）。
未找到匹配时，输出原始字节并将标志位置 1。

### 解压

1. 读取 8 字节头部（解压后大小 + 保留）
2. 逐字节读取标志字节，逐位判断：
   - 位 = 1：读取 1 字节原始数据，写入输出
   - 位 = 0：读取 2 字节匹配引用，从滑动窗口历史位置复制数据

解压在达到头部声明的解压后大小时停止。

## Python API

### `compress(raw_data: bytearray, pack: int = 1) -> bytearray`

压缩原始数据。

| 参数       | 类型        | 默认值 | 说明                                   |
| ---------- | ----------- | ------ | -------------------------------------- |
| `raw_data` | `bytearray` | -      | 要压缩的原始数据                       |
| `pack`     | `int`       | `1`    | 输出对齐（1=不对齐，2/4/8=按字节对齐） |

**示例：**

```python
from core.lzss import compress

data = bytearray(b"Hello, World! Hello, World!")
compressed = compress(data)
```

### `decompress(comp_data: bytearray) -> bytearray`

解压 LZSS 数据。

| 参数        | 类型        | 说明          |
| ----------- | ----------- | ------------- |
| `comp_data` | `bytearray` | LZSS 压缩数据 |

**示例：**

```python
from core.lzss import decompress

raw = decompress(compressed)
```

## 实现

底层 C 扩展 `_lzss` 通过 CPython C API 编写：

- `lzss.c` — 压缩/解压核心实现 + Python C API 包装
- `lzss.h` — C 层接口声明
- `_lzss.pyi` — 类型存根

Python 包装层 `core.lzss` 直接从 `_lzss` 导出 `compress` / `decompress`。

## 构建

```bash
# 项目根目录统一构建（推荐）
python build_project.py

# 或手动编译
cd src/core/lzss
python setup.py build_ext --inplace
```

## 依赖

- Python ≥ 3.12
- CPython 开发头文件
