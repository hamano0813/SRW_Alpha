# Rom 观察者模式 — 全局索引数据同步机制

## 概述

UI 中的下拉框、表格、解释面板等控件需要引用三类全局数据：

| 数据 | 类型 | 来源 | 用途 |
|------|------|------|------|
| `robots` | `dict[int, str]` | `ROBOT.RAF` 每条机体的 `rname` | 机体选择、SNDATA 指令解释 |
| `pilots` | `dict[int, str]` | `PILOT.BIN` 每条驾驶员的 `nname` | 驾驶员选择、SNDATA 指令解释 |
| `snmsgs` | `list[str]` | `SNMSG.BIN` 每条消息的 `snmsg` | 消息引用、SNDATA 指令解释 |

这些数据在编辑器中可能被修改（主要是表格第一列直接写 `data` 字典），
修改后需要自动通知所有正在使用这些数据的 UI 控件刷新。
为此 `Rom` 类内置了一套**观察者模式**，不依赖 Qt 信号槽。

## 操作链条

```
编辑表格第一列
    │
    ▼
FixedTableModel.setData()  ── col!=0 → 跳过
    │ col==0
    ▼
columnZeroEdited 信号
    │
    ▼
FixedTableView.columnZeroEdited 转发信号
    │
    ▼
Frame 槽函数 → rom.notify("robots")  /  "pilots"  /  "snmsgs"
    │
    ▼
Rom._rebuild(<type>)  ── 全量重建静态缓存字典/列表
    │  base | extras 合并
    ▼
遍历该类型的所有观察者，逐一推送
    │ try/except 自动清理失效观察者
    ▼
各观察者的回调函数收到完整 dict / list，自行刷新界面
```

## 注册与推送

### 注册观察者

```python
rom.observe("robots", self._on_robot_list)
rom.observe("pilots", self._on_pilot_list, extras={
    0x7D0: "[7D0]主人公",
    0x7D1: "[7D1]恋人",
    0x7FA: "[7FA]？？？",
})
rom.observe("snmsgs", self._on_snmsg_list)
```

参数说明：

- `data_type: str` — 观察的数据类型，可选 `"robots"` / `"pilots"` / `"snmsgs"`
- `callback: Callable` — 推送时调用的函数，接收一个参数（合并后的完整 dict/list）
- `extras: dict | None` — **仅 dict 类型使用**。调用者可在此传入一些不在原始数据中的特殊键值对，
  推送时通过 `base | extras` 合并到完整 dict 中返回。
  `extras` 优先级更高，可用于替换或扩充真实条目。

### 取消注册

```python
rom.unobserve("robots", self._on_robot_list)
```

### 触发推送

```python
rom.notify("robots")
```

三个数据类型互不影响，`notify("robots")` 不会触发 pilot 的观察者。

### 批量防抖

粘贴多行数据等场景中，不希望每贴一行就推送一次：

```python
rom.suspend("robots")       # 暂停 robots 推送
for row in clipboard:
    model.setData(...)      # 批量修改，不触发推送
rom.resume("robots")        # 恢复 + 合并推送一次
```

`suspend` 期间收到的 `notify` 请求被记录但暂不处理。
`resume` 时检查是否有暂挂请求，如有则执行一次推送。

## 缓存策略

```python
# 解析完成后立即建立静态副本（在 parse_robots / parse_pilots / parse_snmsgs 末尾自动调用）
self._rebuild("robots")
```

之后的每次 `notify` 都会全量重建缓存：
```python
def _rebuild(self, data_type: str) -> None:
    if data_type == "robots":
        raw = self.data["robots"]["robots"]
        cached = {i: f"[{i:03X}]{r['rname']}" for i, r in enumerate(raw)}
    elif data_type == "pilots":
        raw = self.data["pilots"]["pilots"]
        cached = {i: f"[{i:03X}]{p['nname']}" for i, p in enumerate(raw)}
    elif data_type == "snmsgs":
        raw = self.data["snmsgs"]["snmsgs"]
        cached = [item["snmsg"] for item in raw]
    self._cached[data_type] = cached
```

**属性访问**也是走的缓存（不是每次都实时构建）：
```python
@property
def robots(self) -> dict[int, str]:
    return self._cached.get("robots", {})

@property
def pilots(self) -> dict[int, str]:
    return self._cached.get("pilots", {})

@property
def snmsgs(self) -> list[str]:
    return self._cached.get("snmsgs", [])
```

数据在 `parse_*` 时进缓存，此后只有 `notify` 触发时刷新。

## 格式说明

| 数据类型 | 索引格式 | 示例 |
|----------|----------|------|
| robots | 3 位大写的零填充十六进制 | `{0: "[000]ガンダム", 255: "[0FF]..."}` |
| pilots | 同 robots | `{0: "[000]アムロ", 0x7D0: "[7D0]主人公"}` |
| snmsgs | 直出文本，无序号前缀 | `["１．敵の全滅。", "１．ヱクセリヲンの撃墜。", ...]` |

`robots` 和 `pilots` 使用 `dict` 是因为存在 `extras` 等**不在原始数据中的特殊键**（如程序内存中指定的驾驶员），
`snmsgs` 使用 `list` 且不支持 `extras`。

## 合并顺序

观察者推送时的合并操作：
```python
merged = cached | extras   # Python 3.9+ dict 合并运算符
```

`extras` 的键会覆盖缓存中的同名键（当调用者需要替换某条真实条目时有用）。

## 信号连线（Qt → Rom 的桥梁）

因为 `Rom` 不是 `QObject`，需要各子 Frame 将 Qt 信号转化为 `rom.notify()` 调用。

### FixedTableModel（表格数据模型）

```python
class FixedTableModel(QAbstractTableModel):
    columnZeroEdited = Signal()

    def setData(self, index, value, role=Qt.EditRole):
        ret = super().setData(index, value, role)
        if ret and index.column() == 0:
            self.columnZeroEdited.emit()
        return ret
```

只在**第一列**（名称列）修改时发信号，其他列不触发重建。

### FixedTableView（表格视图）

```python
class FixedTableView(QTableView):
    columnZeroEdited = Signal()

    def setModel(self, model):
        if self.model():
            try: self.model().columnZeroEdited.disconnect(self._forward)
            except RuntimeError: pass
        super().setModel(model)
        if model:
            model.columnZeroEdited.connect(self._forward)

    def _forward(self):
        self.columnZeroEdited.emit()
```

转发信号，避免外部直接依赖 model 类型。

### Frame 侧（以 RobotFrame 为例）

```python
class RobotFrame(ProxyFrame):
    def __init__(self, ...):
        ...
        self._view.columnZeroEdited.connect(self._on_col_zero_edited)

    def _on_col_zero_edited(self):
        rom = self.window().rom
        rom.notify("robots")
```

Frame 通过 `self.window().rom` 获取 MainWindow 上的唯一 Rom 实例。

### 不发信号的场景

`columnZeroEdited` 可以不连接任何槽函数。
例如某个 FixedTableView 虽然用 FixedTableModel，但编辑的列不是名称列，就不需要连接。

## 自动清理

推送时遍历观察者列表，若某个 callback 抛出 `RuntimeError`（通常因为所属 widget 已销毁），
自动将其从注册表中移除。调用者一般不需要手动 `unobserve`。

```python
def _notify(self, data_type: str, merged) -> None:
    survivors = []
    for cb, extras in self._observers.get(data_type, []):
        try:
            cb(merged)
            survivors.append((cb, extras))
        except RuntimeError:
            pass  # widget 已销毁，自动清理
    self._observers[data_type] = survivors
```

## 动机与设计决策

1. **为什么不用 Qt 信号槽来同步？**  
   `Rom` 是纯 Python 数据中枢，不应该耦合 Qt 类型。观察者模式用普通 callable，
   在任何上下文都可订阅（Qt widget、SNDATA 解释器、测试代码）。

2. **为什么全量重建而不是增量补丁？**  
   - 名称修改是低频操作，全量重建性能开销可忽略
   - 逻辑简单，不存在"某条数据忘记更新"的竞态风险
   - `suspend/resume` 可在批量操作时聚合成一次推送

3. **为什么用 `base | extras` 而不是 `{**base, **extras}`？**  
   Python 3.12 下 `|` 运算符由 C 层单字节码完成，对大量观察者推送时性能略优。
   详情见 [PEP 584](https://peps.python.org/pep-0584/)。
