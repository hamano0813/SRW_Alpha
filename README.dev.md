# SRW Alpha ROM Editor — 超级机器人大战α ROM 编辑器

[![Python](https://img.shields.io/badge/Python-≥3.14-blue?logo=python&style=flat&labelColor=013243)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.7+-green?logo=qt&style=flat&labelColor=013243)](https://doc.qt.io/qtforpython-6/)
[![qfluentwidgets](https://img.shields.io/badge/qfluentwidgets-1.9.2+-orange?style=flat&labelColor=013243)](https://qfluentwidgets.com/)

基于 **PySide6** 的 ROM 静态编辑器，专为 **PS 版《超级机器人大战α》** 设计。
目前仅支持日版，汉化版因字库原因暂不支持，游戏数据可通用。

---

## 目录

- [SRW Alpha ROM Editor — 超级机器人大战α ROM 编辑器](#srw-alpha-rom-editor--超级机器人大战α-rom-编辑器)
  - [目录](#目录)
  - [功能一览](#功能一览)
    - [已实现](#已实现)
    - [计划实现](#计划实现)
    - [可能实现](#可能实现)
  - [环境搭建](#环境搭建)
    - [Python 版本](#python-版本)
    - [编译器（C 扩展用）](#编译器c-扩展用)
  - [快速开始](#快速开始)
    - [1. 克隆仓库](#1-克隆仓库)
    - [2. 安装依赖](#2-安装依赖)
    - [3. 构建 C 扩展](#3-构建-c-扩展)
    - [4. 运行](#4-运行)
  - [开发注意事项](#开发注意事项)
    - [编译资源文件](#编译资源文件)
    - [更新翻译](#更新翻译)
  - [项目架构](#项目架构)
    - [项目结构](#项目结构)
    - [ROM 模块设计模式](#rom-模块设计模式)
    - [C 扩展设计模式](#c-扩展设计模式)
    - [编码规范](#编码规范)
  - [ROM 数据格式](#rom-数据格式)
  - [许可](#许可)

---

## 功能一览

### 已实现

- **机体数据编辑** — 属性、地形适性、特殊能力、武装参数、BGM、变形/分离、系列
- **机师数据编辑** — 能力、地形适性、技能、养成、系列
- **场景文本编辑** — 游戏关卡场景内使用的文本编辑
- **原始镜像解析** — ISO 解包与重建（PSX 工具链）
- **多种语言支持** — English / 简体中文 / 日本語

### 计划实现

- **场景流程编辑** — 关卡场景内剧情和各类事件编辑
- **敌方配置编辑** — 关卡场景内敌方配置编辑和AI编辑
- **剧本流程编辑** — 游戏各关卡幕前幕中幕尾流程编辑
- **游戏参数编辑** — 改造幅度、精神消耗、芯片属性、生日精神等参数编辑
- **全角字符重绘** — 对游戏字库进行重绘编辑

### 可能实现

- **游戏图片编辑** — 游戏内各类图片导入导出
- **场景地图编辑** — 对场景地图和出击位置进行编辑
- **游戏音乐编辑** — 游戏内音乐替换
- **其他字符重绘** — 游戏字库使用的多种字体进行重绘编辑
- **汉化版本支持** — 通过加载汉化字库TBL实现汉化版编辑

---

## 环境搭建

### Python 版本

- Python ≥ 3.14
- 包管理器：[uv](https://docs.astral.sh/uv/)

### 编译器（C 扩展用）

项目包含多个 C 扩展（`.pyd`），需要 C 编译器才能构建。

**Windows（MinGW-w64）：**

所有 C 扩展的 `setup.cfg` 默认配置为 `compiler = mingw32`。需要安装 MinGW-w64 并确保 `gcc` 在 `PATH` 中：

- 通过 [MSYS2](https://www.msys2.org/) 安装：`pacman -S mingw-w64-ucrt-x86_64-gcc`
- 或通过 [WinLibs](https://winlibs.com/) 下载 standalone 版本
- 安装后将 `mingw64/bin` 目录添加到系统 `PATH`

验证：

```bash
gcc --version
```

> 如果使用 MSVC 而非 MinGW，需移除各模块的 `setup.cfg` 或将其内容清空，setuptools 会自动检测 MSVC。

**Linux：**

```bash
sudo apt install gcc python3-dev
```

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/Hamano0813/SRW_Alpha.git
cd SRW_Alpha
```

### 2. 安装依赖

```bash
uv sync
```

国内用户可使用阿里云镜像加速：

```bash
uv sync --index-url https://mirrors.aliyun.com/pypi/simple/
```

### 3. 构建 C 扩展

```bash
cd src/core/robot_raf   && uv run python setup.py build_ext --inplace && cd ../../..
cd src/core/dr_bin      && uv run python setup.py build_ext --inplace && cd ../../..
cd src/core/dc_bin      && uv run python setup.py build_ext --inplace && cd ../../..
cd src/core/pilot_bin   && uv run python setup.py build_ext --inplace && cd ../../..
cd src/core/snmsg_bin   && uv run python setup.py build_ext --inplace && cd ../../..
cd src/core/sndata_bin  && uv run python setup.py build_ext --inplace && cd ../../..
cd src/core/lzss        && uv run python setup.py build_ext --inplace && cd ../../..
cd src/core/codec       && uv run python setup.py build_ext --inplace && cd ../../..
```

### 4. 运行

```bash
uv run src/main.py
```

首次启动需在"设置 → ROM 路径"中指定解包后的 ROM 数据目录。

---

## 开发注意事项

### 编译资源文件

Qt 资源文件（`res/res.qrc`）变更后需重新编译：

```bash
pyside6-rcc res/res.qrc -o src/res.py
```

### 更新翻译

```bash
# 从源代码提取翻译字符串
pyside6-lupdate src/ -ts res/i18n/zh_CN.ts res/i18n/ja_JP.ts

# 编译 .ts → .qm（发布用二进制格式）
pyside6-lrelease res/i18n/zh_CN.ts res/i18n/ja_JP.ts

# 或使用 translate.bat 脚本（提取 → 启动 Linguist 编辑 → 编译 → 刷新资源）
.\translate.bat
```

---

## 项目架构

### 项目结构

```tree
SRW_Alpha/
├── src/
│   ├── main.py              # 程序入口，DPI 缩放与应用启动
│   ├── config.py             # 全局配置（QConfig 持久化）
│   ├── res.py                # 编译后的 Qt 资源（由 res.qrc 生成）
│   ├── core/                 # ROM 数据核心
│   │   ├── codec/            #   文本编解码和特殊字符处理
│   │   ├── lzss/             #   LZSS 压缩/解压
│   │   ├── robot_raf/        #   ROBOT.RAF 解析/构建
│   │   ├── dr_bin/           #   DR.BIN 解析/构建
│   │   ├── dc_bin/           #   DC.BIN 解析/构建
│   │   ├── pilot_bin/        #   PILOT.BIN 解析/构建
│   │   ├── snmsg_bin/        #   SNMSG.BIN 解析/构建
│   │   ├── sndata_bin/       #   SNDATA.BIN 解析/构建
│   │   └── rom.py            #   ROM 数据交互中枢
│   ├── gui/                  # 图形界面
│   │   ├── custom/           #   自定义数据（枚举映射和图标资源等）
│   │   ├── widget/           #   编辑控件
│   │   │   ├── abstract/     #     抽象组件（不可实例化）
│   │   │   ├── proxy/        #     代理组件（用于转发信号或进行控件数据分发回收）
│   │   │   ├── common/       #     通用组件（用于普通编辑的组件）
│   │   │   ├── special/      #     专用组件（在特殊情况下使用）
│   │   │   └── table/        #     表格组件（构成可编辑表格的表格本体和模型以及代理组件）
│   │   └── interface/        #   功能页面
│   │       ├── home/         #     首页（加载/保存/解析/重建）
│   │       ├── unit/         #     机体编辑
│   │       ├── pilot/        #     机师编辑
│   │       ├── snmsg/        #     文本编辑
│   │       ├── script/       #     脚本编辑
│   │       ├── sndata/       #     场景编辑
│   │       ├── dictionary/   #     图鉴编辑
│   │       └── option/       #     设置选项
│   └── utils/                # 工具函数
├── res/                      # 资源文件
│   ├── bin/                  #   ROM 开发用数据缓存
│   ├── icon/                 #   界面图标（SVG）
│   ├── i18n/                 #   翻译文件（.ts / .qm）
│   └── splash/               #   启动画面图片
├── tools/                    # PSX 工具
│   ├── dumpsxiso.exe         #   ISO 解包
│   └── mkpsxiso.exe          #   ISO 打包
└── pyproject.toml            # 项目配置与依赖
```

### ROM 模块设计模式

`core/rom.py` 的 `Rom` 类采用三级分发管理各文件类型：

```python
_FILE_PATHS: dict[str, str] = {
    "robots": "UNITPRAM/ROBOT.RAF",
}
_LOAD_DISPATCH: dict[str, str] = {
    "robots": "load_robots",
}
_SAVE_DISPATCH: dict[str, str] = {
    "robots": "save_robots",
}
```

- `_FILE_PATHS` — 文件 key → 缓存目录下相对路径
- `_LOAD_DISPATCH` — key → `load_*` 方法（`read_cache()` 分发）
- `_SAVE_DISPATCH` — key → `save_*` 方法（`write_cache()` 分发）

新增文件类型时需同步更新上述三个字典并添加对应的 `load_*`/`save_*` 方法。

### C 扩展设计模式

各 C 模块对外暴露对称的 `parse`/`build` 接口：

```python
data: dict = parse(data_bytes)       # 二进制 → Python 对象
data_bytes: bytearray = build(data)  # Python 对象 → 二进制
```

内部按两层拆分：

```type
第一层（纯二进制，不碰 Python 对象）：
  _entries_decompress()  — 原始文件 → 中间态
  _entries_compress()    — 中间态 → 原始文件

第二层（在 parse/build 中内联）：
  _destruct_*()          — 中间态 → Python dict（字段移位拆包）
  _structure_*()         — Python dict → 中间态（字段移位打包）
```

第一层与第二层独立。各 C 扩展目录下的 `README.md` 有详细的数据结构和 API 说明。

### 编码规范

项目遵循 Python 标准规范，补充约定：

- 模块文件头必须包含 docstring
- 公开方法使用 `"""docstring"""`，私有方法至少一句中文注释
- 行内注释使用中文，优先写"为什么"而非"是什么"
- 代码已自明的部分不加注释
- 中英文不混用

---

## ROM 数据格式

解包后所需文件及用途：

| 文件        | 用途     |
| ----------- | -------- |
| ROBOT.RAF   | 机体数据 |
| PILOT.BIN   | 机师数据 |
| SNMSG.BIN   | 场景文本 |
| SNDATA.BIN  | 场景数据 |
| ENLIST.BIN  | 敌方配置 |
| AIUNP.BIN   | AI 设计  |
| SCRIPT.BIN  | 脚本文本 |
| PRM_GRP.BIN | 参数组   |
| 12F.DAT     | 全角字符 |
| DR.BIN      | 机体图鉴 |
| DC.BIN      | 机师图鉴 |

游戏内文本使用 **Shift-JIS (x0213)** 编码。`src/core/codec/` 提供完整编解码支持。

---

## 许可

本项目仅供学习与研究目的。使用前请确保拥有《超级机器人大战α》的合法拷贝。
