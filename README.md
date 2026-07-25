# SRW Alpha ROM Editor — 超级机器人大战α ROM 编辑器

[![Python](https://img.shields.io/badge/Python-≥3.14-blue?logo=python&style=flat&labelColor=013243)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.7+-green?logo=qt&style=flat&labelColor=013243)](https://doc.qt.io/qtforpython-6/)
[![qfluentwidgets](https://img.shields.io/badge/qfluentwidgets-1.9.2+-orange?style=flat&labelColor=013243)](https://qfluentwidgets.com/)

基于 **PySide6** 的 ROM 静态编辑器，专为 **PS 版《超级机器人大战α》** 设计。
提供现代化图形界面，支持编辑游戏内机体、机师、武器、消息文本、战场配置、敌方 AI、剧情分支等数据。
目前仅支持日版。汉化版因字库原因暂不支持，游戏数据可通用。

---

## 功能一览

### 已实现

- **机体编辑** — 属性、地形适性、特殊能力、武装参数、BGM、变形/分离、系列
- **机师编辑** — 能力、地形适性、技能、养成、系列
- **场景文本编辑** — 游戏关卡内文本编辑
- **镜像解析** — ISO 解包与重建
- **多种语言界面** — English / 简体中文 / 日本語

### 计划实现

- 场景流程编辑（剧情事件、敌方配置、AI）
- 剧本流程编辑（幕前幕中幕尾流程）
- 游戏参数编辑（改造幅度、精神消耗、芯片属性等）
- 全角字符重绘

---

## 下载与使用

从 [Releases](https://github.com/hamano0813/SRW_alpha/releases) 页面下载最新版本安装程序，运行安装后即可使用。

首次启动需在"设置 → ROM 路径"中指定解包后的 ROM 数据目录。

---

## ROM 数据准备

1. 准备《超级机器人大战α》的 PS1 光盘镜像（.bin/.cue 或 .iso）
2. 使用 PSX 工具解包镜像（如 `dumpsxiso`）
3. 在编辑器中指定解包后的目录即可读取

所需文件由编辑器自动识别，无需手动配置。

---

## 修改说明

> 修改有风险，请自行备份好原文件。

- 载入 ROM 后即可开始编辑，修改后点击写入暂存
- 切换窗口时会提示是否保存，退出前不要忘记保存 ROM
- 大多数表格支持 Ctrl+C / Ctrl+V，可与 Excel 交互进行批量修改

---

## 许可

本项目仅供学习与研究目的。使用前请确保拥有《超级机器人大战α》的合法拷贝。
