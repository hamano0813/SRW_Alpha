# 数据模型设计

## 概述

本目录存放 ROM 编辑器所需的 Qt Model/View 架构中的 Model 层。所有模型均遵循以下核心原则：

- **初始化时不带数据**，通过 `set_data()` 统一装入
- **列标题通过 `set_title()` 注入**，支持运行时更换语言/标题
- **字段与数据的映射**：列索引 → 字段显示名（`self.tr()` 翻译后）→ 唯一 key → row dict 中的值

## 共通的字段映射机制

### 数据结构

每一行数据均为一个 `dict`，字段 key 与显示的列标题分离。由 `fields.py` 中的 `FieldMapping` 提供翻译后的映射关系：

```python
# fields 定义：key/value 均已通过 self.tr() 翻译
fields = {
    "名称":   "rname",     # 表头文字: 数据 key
    "Lv":     "lv",
    "HP":     "hp",
}

# 行数据示例（key 对应的是 fields 的 value）
row = {
    "rname": "ゲッター1",
    "lv": 99,
    "hp": 65000,
    "weapons": [...],    # 子列表字段
}
```

### 索引流程

```code
set_title(fields) 时：
  _fields = {tr(表头): 数据 key, ...}
  _titles = [tr(表头), ...]   ← 按传入 dict 的插入顺序

data()/setData() 时：
  列索引 i → _titles[i]（表头）→ _fields[表头]（数据 key）→ row_dict[key]
```

---

## 模型分类

### 1. 不可增删表格模型（`FixedTableModel`）

**用途：** 展示各类固定行数的结构化数据，如机体列表、驾驶员列表、武器列表等。

| 特性       | 说明                                                                                                            |
| ---------- | --------------------------------------------------------------------------------------------------------------- |
| 行数       | 固定，用户不可增删                                                                                              |
| 单元格编辑 | 支持原地编辑，通过自定义 Delegate 实现                                                                          |
| 排序       | 支持（点击列头排序）                                                                                            |
| 过滤       | 支持（通过 QSortFilterProxyModel）                                                                              |
| 搜索       | 支持（通过 QSortFilterProxyModel 的 setFilterFixedString / setFilterRegularExpression）                         |
| 信号发射   | 单击某行时，将该行索引作为信号发出，驱动外部的 QDataMapperWidget 编辑器                                         |
| 子表格联动 | 某列的数据若为子列表（如 weapons），可将该子列表发送至子表格；子表格还可进一步控制子 QDataMapperWidget 的编辑器 |

**编辑器类型配置：**

通过 `set_editors({数据 key: 编辑器类型, ...})` 独立配置，不混入 `set_title`。

**原地编辑支持的数据类型：**

- **文本** — 字符串编辑（`QLineEdit`）
- **整数** — 正负整数编辑（`QSpinBox`）
- **浮点数** — 正负小数编辑（`QDoubleSpinBox`）

以上通过 `FieldDelegate` 按列自动选择，不需要为每列单独设置 Delegate。

**信号/联动机制：**

```tree
FixedTableModel
  │
  ├─ 单击行 → 信号 emit(row_index)
  │              └→ QDataMapperWidget 的各编辑器（QLineEdit/QSpinBox 等）
  │                 读取该行对应字段的值并显示
  │
  └─ 子列表列 → 信号 emit(row_index, field_key)
                   └→ 子表格（嵌套的 QTableView）
                       │
                       └─ 单击子表格行 → 信号 emit(sub_row_index)
                                           └→ 子 QDataMapperWidget 的编辑器
```

子表格的联动深度无限制，但实际使用通常不超过两级（主表 → 子表 → 子表的编辑器）。

### 2. 可增删表格模型（`MutableTableModel`）

**用途：** 展示可动态编辑的命令列表，主要为 SNDATA.BIN 中的 command 流编辑服务。

| 特性       | 说明                                     |
| ---------- | ---------------------------------------- |
| 行数       | 用户可追加、插入、删除条目               |
| 单元格编辑 | **不支持原地编辑**，双击行弹出子窗口编辑 |
| 排序       | 不支持（命令流顺序有意义）               |
| 过滤       | 支持（通过 QSortFilterProxyModel）       |
| 搜索       | 支持                                     |

**编辑方式：**

```tree
双击行（或右键菜单）
       │
       └→ 弹出子窗口（QDialog）
              │
              ├─ 展示该行 command 的全体参数
              ├─ 用户修改各字段
              └─ 确认 → 更新模型数据
```

**适用场景：**

- SNDATA.BIN 的场景指令（command）编辑
- 其他需要用户控制条目数量的列表数据

---

## 模型 API 设计约定（草案）

所有模型约定以下公开接口：

`set_data(data: list[dict])`
装入列表数据。每项为一个 dict。

`set_title(fields: list[tuple[str, str]])`
设置列标题和内部映射。每项为 `(key, display_name)`。

- `key` — 对应 row dict 中的实际键名
- `display_name` — 列标题原文，传入后立即通过 `self.tr()` 翻译

可在任意时刻重复调用以切换标题/语言。

`data()`, `setData()`, `rowCount()`, `columnCount()`
标准 Qt 模型接口，按列索引 → 显示名 → key → row dict 的链路取/写数据。

`flags()`

- 不可增删表格：`Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable`
- 可增删表格：`Qt.ItemIsEnabled | Qt.ItemIsSelectable`（编辑不走原地）

---

## 信号设计（草案）

### 不可增删表格信号

| 信号                                       | 说明                                        |
| ------------------------------------------ | ------------------------------------------- |
| `rowSelected(int row)`                     | 单击行，通知外部 QDataMapperWidget 加载该行 |
| `subListRequested(int row, str field_key)` | 请求将某行的子列表字段发送至子表格          |

### 可增删表格信号

| 信号                         | 说明                             |
| ---------------------------- | -------------------------------- |
| `itemDoubleClicked(int row)` | 双击某行，通知外部弹出编辑子窗口 |

---

## 目录文件约定

```tree
models/
├── README.md              # 本文件
├── __init__.py
├── base_model.py         # 共用基类（字段映射、标题管理等）
├── fixed_model.py        # 固定行数表格模型 + FieldDelegate
└── mutable_model.py      # 可增删行数表格模型
```

基类 `BaseTableModel` 封装字段映射逻辑，两个具体模型继承自它。

---

## 开放问题 / 待定项

1. **子表格联动时数据同步** — 主表某行数据被替换时，子表格是否自动跟随切换？需要建立 observer 模式还是依赖信号槽？
2. **QDataMapperWidget 的编辑器自动绑定** — 单击行信号发出后，如何自动将行数据分发到各编辑器？是外部槽函数逐个 setText/setValue，还是用一个通用的 setDataMapper(row_data) 方法？
3. **拖拽调整列顺序 / 隐藏列** — 是否需要支持？
4. **数值 Delegate 的校验规则** — 是否支持最小值/最大值约束？范围信息从哪里获取（从字段元数据？）？
5. **过滤/搜索在可增删表格中的交互** — 过滤时行号是否随过滤结果重新编号？删除操作时以原始行号为准还是当前显示行号为准？
6. **子窗口编辑器的 layout 生成** — 是根据 command 的字段类型（code + count + params）自动生成编辑控件，还是手写每个场景？
