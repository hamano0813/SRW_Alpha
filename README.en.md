# SRW Alpha ROM Editor — Super Robot Wars α ROM Editor

[![Python](https://img.shields.io/badge/Python-≥3.14-blue?logo=python&style=flat&labelColor=013243)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.7+-green?logo=qt&style=flat&labelColor=013243)](https://doc.qt.io/qtforpython-6/)
[![uv](https://img.shields.io/badge/uv-0.6+-261230?logo=data:image/svg%2bxml;base64,PHN2ZyB3aWR0aD0iNDEiIGhlaWdodD0iNDEiIHZpZXdCb3g9IjAgMCA0MSA0MSIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTS01LjI4NjE5ZS0wNiAwLjE2ODYyOUwwLjA4NDMwOTggMjAuMTY4NUwwLjE1MTc2MiAzNi4xNjgzQzAuMTYxMDc1IDM4LjM3NzQgMS45NTk0NyA0MC4xNjA3IDQuMTY4NTkgNDAuMTUxNEwyMC4xNjg0IDQwLjA4NEwzMC4xNjg0IDQwLjA0MThMMzEuMTg1MiA0MC4wMzc1QzMzLjM4NzcgNDAuMDI4MiAzNS4xNjgzIDM4LjIwMjYgMzUuMTY4MyAzNlYzNkwzNy4wMDAzIDM2TDM3LjAwMDMgMzkuOTk5Mkw0MC4xNjgzIDM5Ljk5OTZMMzkuOTk5NiAtOS45NDY1M2UtMDdMMjEuNTk5OCAwLjA3NzU2ODlMMjEuNjc3NCAxNi4wMTg1TDIxLjY3NzQgMjUuOTk5OEwyMC4wNzc0IDI1Ljk5OThMMTguMzk5OCAyNS45OTk4TDE4LjQ3NzQgMTYuMDMyTDE4LjM5OTggMC4wOTEwNTkzTC01LjI4NjE5ZS0wNiAwLjE2ODYyOVoiIGZpbGw9IiNERTVGRTkiLz4KPC9zdmc+&logoColor=white&style=flat&labelColor=013243)](https://github.com/astral-sh/uv)
[![MinGW-w64](https://img.shields.io/badge/MinGW--w64-14+-2E8B57?logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMzIgMTMyIj4KPGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoLTIzLjM1NiAtMTcuMDI5KSI+CjxyZWN0IHRyYW5zZm9ybT0icm90YXRlKC00NSkiIHg9Ii0zMi4wMjQiIHk9IjY1LjA1NCIgd2lkdGg9IjMyLjUyOSIgaGVpZ2h0PSIzMi41MjkiIGZpbGw9IiM5OTkiLz4KPHJlY3QgdHJhbnNmb3JtPSJyb3RhdGUoLTQ1KSIgeD0iLTcyLjQ5IiB5PSIxMDUuNTIiIHdpZHRoPSIzMi41MjkiIGhlaWdodD0iMzIuNTI5IiBmaWxsPSIjOTk5Ii8+CjxyZWN0IHRyYW5zZm9ybT0icm90YXRlKC00NSkiIHg9Ii0zMi4wMjQiIHk9IjEwNS41MiIgd2lkdGg9IjMyLjUyOSIgaGVpZ2h0PSIzMi41MjkiIGZpbGw9IiM0ZDRkNGQiLz4KPHJlY3QgdHJhbnNmb3JtPSJyb3RhdGUoLTQ1KSIgeD0iOC40NDIzIiB5PSI2NS4wNTQiIHdpZHRoPSIzMi41MjkiIGhlaWdodD0iMzIuNTI5IiBmaWxsPSIjNGQ0ZDRkIi8+CjxyZWN0IHRyYW5zZm9ybT0icm90YXRlKC00NSkiIHg9IjguNDQyMyIgeT0iMTA1LjUyIiB3aWR0aD0iMzIuNTI5IiBoZWlnaHQ9IjMyLjUyOSIgZmlsbD0iIzk5OSIvPgo8cmVjdCB0cmFuc2Zvcm09InJvdGF0ZSgtNDUpIiB4PSI0OC45MDgiIHk9IjEwNS41MiIgd2lkdGg9IjMyLjUyOSIgaGVpZ2h0PSIzMi41MjkiIGZpbGw9IiM0ZDRkNGQiLz4KPHJlY3QgdHJhbnNmb3JtPSJyb3RhdGUoLTQ1KSIgeD0iLTMyLjAyNCIgeT0iMTQ1Ljk5IiB3aWR0aD0iMzIuNTI5IiBoZWlnaHQ9IjMyLjUyOSIgZmlsbD0iIzk5OSIvPgo8cmVjdCB0cmFuc2Zvcm09InJvdGF0ZSgtNDUpIiB4PSI4LjQ0MjMiIHk9IjE0NS45OSIgd2lkdGg9IjMyLjUyOSIgaGVpZ2h0PSIzMi41MjkiIGZpbGw9IiM0ZDRkNGQiLz4KPC9nPgo8L3N2Zz4=&logoColor=white&style=flat&labelColor=013243)](https://www.mingw-w64.org/)
[![Inno Setup](https://img.shields.io/badge/Inno%20Setup-6.4+-blue?logo=data:image/svg%2bxml;base64,PHN2ZyB2aWV3Qm94PSIwIDAgMzIgMzIiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxkZWZzPjxyYWRpYWxHcmFkaWVudCBpZD0iYSIgY3g9IjE2LjYzNyIgY3k9IjE2IiByPSIxMi40NiIgZ3JhZGllbnRVbml0cz0idXNlclNwYWNlT25Vc2UiPjxzdG9wIG9mZnNldD0iMCIgc3RvcC1jb2xvcj0iI2Q4ZmZmZiIvPjxzdG9wIG9mZnNldD0iMC4xMTMiIHN0b3AtY29sb3I9IiNhZmU5ZmEiLz48c3RvcCBvZmZzZXQ9IjAuMjM5IiBzdG9wLWNvbG9yPSIjODdkM2Y0Ii8+PHN0b3Agb2Zmc2V0PSIwLjMzOSIgc3RvcC1jb2xvcj0iIzZmYzZmMSIvPjxzdG9wIG9mZnNldD0iMC40IiBzdG9wLWNvbG9yPSIjNjZjMWYwIi8+PHN0b3Agb2Zmc2V0PSIwLjQ3MyIgc3RvcC1jb2xvcj0iIzYwYjllNyIvPjxzdG9wIG9mZnNldD0iMC41OTEiIHN0b3AtY29sb3I9IiM1MGEzY2YiLz48c3RvcCBvZmZzZXQ9IjAuNzQxIiBzdG9wLWNvbG9yPSIjMzc3ZmE3Ii8+PHN0b3Agb2Zmc2V0PSIwLjkxNSIgc3RvcC1jb2xvcj0iIzEzNGU3MCIvPjxzdG9wIG9mZnNldD0iMSIgc3RvcC1jb2xvcj0iIzAwMzQ1MyIvPjwvcmFkaWFsR3JhZGllbnQ+PGxpbmVhckdyYWRpZW50IGlkPSJiIiB4MT0iMjAuNjIzIiB5MT0iMjYuOTk5IiB4Mj0iMTEuNTg5IiB5Mj0iMTEuMzUyIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+PHN0b3Agb2Zmc2V0PSIwIiBzdG9wLWNvbG9yPSIjMDAzNDUzIi8+PHN0b3Agb2Zmc2V0PSIwLjc4IiBzdG9wLWNvbG9yPSIjMGY0OTZhIi8+PHN0b3Agb2Zmc2V0PSIwLjg4NyIgc3RvcC1jb2xvcj0iIzY2YzFmMCIvPjxzdG9wIG9mZnNldD0iMSIgc3RvcC1jb2xvcj0iI2JlZmZmZiIvPjwvbGluZWFyR3JhZGllbnQ+PC9kZWZzPjxwYXRoIGQ9Ik0yOS4xLDE2QTEyLjQ2LDEyLjQ2LDAsMSwxLDE2LjYzNywzLjU0LDEyLjQ2LDEyLjQ2LDAsMCwxLDI5LjEsMTZaIiBmaWxsPSJ1cmwoI2EpIi8+PHBhdGggZD0iTTIzLjY3LDEzLjExMUgzMHY3LjE1NWwtMy41NzUsMy4zODNWMTguOTM1bC0xLjM0LDEuNWEyNC4zMjYsMjQuMzI2LDAsMCwxLTguNTI0LDUuODQxLDI3LjgxLDI3LjgxLDAsMCwxLTcuMDE5LDEuOTM4LDIxLjMxNSwyMS4zMTUsMCwwLDEtMy4wMzUtLjAzNmMtMi4yNTctLjQ0NC00LTEuNzUyLTQuMjg0LTMuMTdhNS44NzMsNS44NzMsMCwwLDEtLjAzMi0zLjA5NCwxMS4yLDExLjIsMCwwLDEsMS40MzItMy4xOSwyMC4wNywyMC4wNywwLDAsMSw1Ljg1LTYuMTUzLDM5LjQ4MywzOS40ODMsMCwwLDAtMi43NTcsNC42NjksOS42NDYsOS42NDYsMCwwLDAtLjkwNiwyLjczMiwyLjM5MiwyLjM5MiwwLDAsMCwuNDI2LDEuOTYsNC42NDYsNC42NDYsMCwwLDAsMy44OSwxLjU0NCwxOS44MTgsMTkuODE4LDAsMCwwLDcuMzc1LTEuOCwyMy41MTMsMjMuNTEzLDAsMCwwLDUuOTQ5LTMuNjc0bDEuNC0xLjMyNy00LjYuMDQ3WiIgZmlsbD0iI2ZmZiIvPjxwYXRoIGQ9Ik0yOS41MTgsMTMuNTkzdjYuNDY2TDI2LjkwNywyMi41M1YxNy42NzFsLS44NDIuOTQ0LTEuMzQsMS41YTIzLjgzMiwyMy44MzIsMCwwLDEtOC4zNTMsNS43MTgsMjcuMTY2LDI3LjE2NiwwLDAsMS02Ljg3NiwxLjljLS4yMjEuMDIxLS42OTMuMDM1LTEuMjMyLjAzNUExMy45MjksMTMuOTI5LDAsMCwxLDYuNiwyNy43MDhjLTIuMDE2LS40LTMuNjU5LTEuNTcxLTMuOS0yLjc5MkE1LjQ2Myw1LjQ2MywwLDAsMSwyLjY2NiwyMmExMC43MDgsMTAuNzA4LDAsMCwxLDEuMzU5LTMuMDA3LDIzLjEsMjMuMSwwLDAsMSwzLjU1OS00LjM1Yy0uNTM1Ljg5NS0uOTg0LDEuNzE2LTEuMywyLjM5NGExMC4wNTUsMTAuMDU1LDAsMCwwLS45NDgsMi44NzMsMi44ODMsMi44ODMsMCwwLDAsLjUxNSwyLjMxLDUuMSw1LjEsMCwwLDAsNC4yNzgsMS43NDFBMjAuMTgyLDIwLjE4MiwwLDAsMCwxNy43LDIyLjEyMmEyNC4wMzQsMjQuMDM0LDAsMCwwLDYuMDgyLTMuNzYzbDEuNC0xLjMyOC44ODktLjg0NC0xLjIyNi4wMTMtMy40NjMuMDM2LDIuNS0yLjY0M2g1LjY0MU05LjQ3MywxMi41NzRhMjAuMDcsMjAuMDcsMCwwLDAtNS44NSw2LjE1MywxMS4yLDExLjIsMCwwLDAtMS40MzIsMy4xOSw1Ljg3Myw1Ljg3MywwLDAsMCwuMDMyLDMuMDk0Yy4yODYsMS40MTgsMi4wMjcsMi43MjYsNC4yODQsMy4xN2ExNC4zOTEsMTQuMzkxLDAsMCwwLDEuNzU3LjA3M2MuNTI3LDAsMS4wMjYtLjAxMywxLjI3OC0uMDM3YTI3LjgxLDI3LjgxLDAsMCwwLDcuMDE5LTEuOTM4LDI0LjMyNiwyNC4zMjYsMCwwLDAsOC41MjQtNS44NDFsMS4zNC0xLjV2NC43MTRMMzAsMjAuMjY2VjEzLjExMUgyMy42N2wtMy40MjIsMy42MTgsNC42LS4wNDctMS40LDEuMzI3QTIzLjUxMywyMy41MTMsMCwwLDEsMTcuNSwyMS42ODNhMTkuODE4LDE5LjgxOCwwLDAsMS03LjM3NSwxLjgsNC42NDYsNC42NDYsMCwwLDEtMy44OS0xLjU0NCwyLjM5MiwyLjM5MiwwLDAsMS0uNDI2LTEuOTYsOS42NDYsOS42NDYsMCwwLDEsLjkwNi0yLjczMiwzOS40ODMsMzkuNDgzLDAsMCwxLDIuNzU3LTQuNjY5WiIgZmlsbD0idXJsKCNiKSIvPjwvc3ZnPg==&logoColor=white&style=flat&labelColor=013243)](https://jrsoftware.org/isinfo.php)
[![PlayStation](https://img.shields.io/badge/PlayStation-1-003791?logo=playstation&logoColor=white&style=flat&labelColor=013243)](https://www.playstation.com/)
[![Windows](https://img.shields.io/badge/Windows-10%2B-00A4EF?logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIGhlaWdodD0iODgiIHdpZHRoPSI4OCIgeG1sbnM6dj0iaHR0cHM6Ly92ZWN0YS5pby9uYW5vIj48cGF0aCBkPSJNMCAxMi40MDJsMzUuNjg3LTQuODYuMDE2IDM0LjQyMy0zNS42Ny4yMDN6bTM1LjY3IDMzLjUyOWwuMDI4IDM0LjQ1M0wuMDI4IDc1LjQ4LjAyNiA0NS43em00LjMyNi0zOS4wMjVMODcuMzE0IDB2NDEuNTI3bC00Ny4zMTguMzc2em00Ny4zMjkgMzkuMzQ5bC0uMDExIDQxLjM0LTQ3LjMxOC02LjY3OC0uMDY2LTM0LjczOXoiIGZpbGw9IiMwMGFkZWYiLz48L3N2Zz4=&logoColor=white&style=flat&labelColor=013243)](https://www.microsoft.com/windows)
[![GitHub Release](https://img.shields.io/github/v/release/hamano0813/SRW_Alpha?label=Release&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDI0IDEwMjQiPjxwYXRoIGQ9Ik01MTIgNTEybS01MTIgMGE1MTIgNTEyIDAgMSAwIDEwMjQgMCA1MTIgNTEyIDAgMSAwLTEwMjQgMFoiIGZpbGw9IiNGQTg5MTkiPjwvcGF0aD48cGF0aCBkPSJNNzk4LjcyIDM3MC4zMzZjLTIwLjczNiAxOS41Mi00MC42NCA0My4yLTU5LjYxNiA3MS4xMDQtMi41Ni0zNS41Mi05LjA1Ni02NS42LTE5LjQyNC05MC4xNDQgMTMuODI0LTE2Ljg5NiAyNy42NDgtMzEuNzEyIDQxLjQ3Mi00NC40MTYgOC42NCAxMS44NCAyMS4xMiAzMi45OTIgMzcuNTY4IDYzLjQ1Nm0tMTk1LjYxNiAyNTAuMDhjMCAyMS4xODQgNS4xODQgNDUuMjggMTUuNTUyIDcyLjM1MmwyLjU2IDguODk2Yy0zNy4xMiAzOS44MDgtODMuMzI4IDYxLjc2LTEzOC41NiA2Ni4wMTZhMTk3Ljc2IDE5Ny43NiAwIDAgMS04Ny40NTYtMTUuMjMyIDIxNS4xMzYgMjE1LjEzNiAwIDAgMS03NS43NzYtNTIuMDY0Yy0yMy4yOTYtMjUuMzc2LTQwLjM1Mi01NS42MTYtNTEuMTY4LTkwLjc1Mi0xMC43ODQtMzUuMTA0LTE0LjQ2NC03My40MDgtMTEuMDA4LTExNC44OCA2LjkxMi02MC4wNjQgMjguNzA0LTExMS40ODggNjUuNDQtMTU0LjI0IDM2LjY3Mi00Mi43MiA4MC45Ni02OS4xODQgMTMyLjc2OC03OS4zNiA1NC40LTExLjg0IDEwNy41Mi0zLjM2IDE1OS4zMjggMjUuNDA4IDI3LjYxNiAxNi45NiA0OC43NjggMzguNzIgNjMuNDU2IDY1LjM3NiAxNC42ODggMjYuNjU2IDIzLjc0NCA1OC4yMDggMjcuMiA5NC41OTIgMS43MjggOS4yOCAyLjE0NCAyMy4yNjQgMS4yOCA0MS44ODhsLTEuMjggNTkuNjQ4YzAgMzEuMzI4IDEuNzI4IDU1LjQ1NiA1LjE4NCA3Mi4zNTIgNC4zMiAyNC41NzYgMTMuMzc2IDQxLjkyIDI3LjIgNTIuMDY0IDEwLjM2OCA4LjQ0OCAyMi44OCAxMi4yNTYgMzcuNTY4IDExLjQyNCAxMS4yIDAgMTkuNDI0LTIuNTYgMjQuNjA4LTcuNjE2LTExLjIzMiAyNC41NDQtMjUuNDcyIDQyLjMwNC00Mi43NTIgNTMuMzEyLTE0LjY4OCA5LjMxMi0zMC4yNCAxMy4xMi00Ni42MjQgMTEuNDI0LTEzLjgyNC0xLjY5Ni0yNS4wNTYtNi4zMzYtMzMuNjY0LTEzLjk1Mi0xNC43Mi0xMy41MzYtMjUuOTItMzguNTI4LTMzLjY5Ni03NC45MTItNy43NzYtMzQuNjg4LTExLjY0OC03NC4wNDgtMTEuNjQ4LTExOC4wOHYtMTMuOTUyYzAtMjguNzM2LTAuODY0LTUwLjc1Mi0yLjU5Mi02NS45ODQtMi41OTItMjUuNDA4LTguMjI0LTQ2LjMzNi0xNi44MzItNjIuODQ4YTEwNS4zNzYgMTA1LjM3NiAwIDAgMC0zNi4yODgtNDBjLTI2Ljc4NC0xNC4zNjgtNTMuNTM2LTIxLjEyLTgwLjMyLTIwLjI4OGExNDAuNjA4IDE0MC42MDggMCAwIDAtNzUuMTA0IDI0LjczNiAxOTQuNTI4IDE5NC41MjggMCAwIDAtNTguMzA0IDYyLjIwOCAyMDYuNzIgMjA2LjcyIDAgMCAwLTI4LjQ4IDg0LjQxNmMtNi4wOCA2MS43NiA4LjE5MiAxMTAuODggNDIuNzIgMTQ3LjI2NCAxMy44MjQgMTQuNCAyOS43OTIgMjUuMzc2IDQ3LjkzNiAzMi45OTIgMTguMTQ0IDcuNjE2IDM1Ljg0IDExLjAwOCA1My4xMiAxMC4xNDQgMjUuMDI0LTEuNjY0IDQ0LjY3Mi01LjY5NiA1OC45NDQtMTIuMDMyIDE0LjI0LTYuMzY4IDI4LjY3Mi0xNi43MDQgNDMuMzkyLTMxLjEwNCA2Ljg4LTYuNzg0IDE0LjY1Ni0xNi41MTIgMjMuMjk2LTI5LjIxNiIgZmlsbD0iI0ZGRkZGRiI+PC9wYXRoPjwvc3ZnPg==&style=flat&labelColor=013243)](https://github.com/hamano0813/SRW_Alpha/releases)

A ROM static editor built on **PySide6**, designed exclusively for the **PS1 version of Super Robot Wars α**

Supports editing of in-game units, pilots, weapons, dialogue text, scenario configurations, enemy AI, story branches, and more.

Currently supports the Japanese version only. The Chinese localized version is not yet supported due to font encoding limitations, though game data is compatible.

---

## Feature Overview

### Implemented

- **Unit Data Editing** — stats, terrain adaptation, special abilities, weapon parameters, BGM, transformation/separation, series
- **Pilot Data Editing** — stats, terrain adaptation, skills, growth, series
- **Scenario Text Editing** — in-game stage dialogue editing
- **ISO File Handling** — ISO extraction and rebuilding
- **Multi-language UI** — English / 简体中文 / 日本語

### Planned

- Scenario Flow Editing — story events, enemy deployments, AI
- Script Flow Editing — pre-stage, mid-stage, post-stage flow
- Game Parameter Editing — upgrade scaling, spirit point costs, chip attributes, etc.
- Full-width Glyph Redrawing — tools to redraw the in-game font

---

## Download & Usage

Two types of packages are available on the [Releases](https://github.com/hamano0813/SRW_Alpha/releases) page:

- **Full installation** (e.g. `SRW_Alpha_v0.x.x.zip`): Contains the editor, runtime, and all dependencies. Extract and run the installer to set up (internet connection required, may take a few minutes).
- **Update package** (e.g. `v0.x.x.zip`): Contains only updated files. Ideal for users who already have an older version. Extract and overwrite the program directory manually.

---

## ROM Preparation

1. Prepare a Japanese PS1 disc image of Super Robot Wars α (.bin/.cue)
2. Configure the source ROM file path and the target ROM file path in Settings

All required module files are automatically extracted by the editor into its cache directory — no manual setup needed.

---

## Instructions

> Editing carries risks. Please back up your files before making changes.

- **Overview > Extract ROM** — Extract the ROM into cache files stored in the editor's directory.
- **Overview > Parse Cache** — Parse game data from cache files, enabling editing features.
- **Overview > Build Cache** — Write edited data back to the cache files.
- **Overview > Rebuild ROM** — Rebuild the cache into a ROM file at the configured output path.
- **Unit > Unit Name, Unit Data, Transformation/Combination, Equipment Swap, Terrain Adaptation, Special Abilities, Cross-Ride System, BGM** — All editable.
  - Transformation: Determined by the transformation group number. Units sharing the same group number can transform between each other. The transformation order is determined by the transformation index. Minimum group number is 1, upper limit unknown. Index range 0-2, supports 3-stage transformation.
  - Combination: Two modes available:
    - Core Fighter Mode: Combination group number 0. Only the base unit needs configuration — the Core Fighter side does not. The base unit's combination count is 1, select the Core Fighter as the core unit.
    - Parts Combination Mode: Determined by the combination group number. Each part unit must be configured individually. Units sharing the same group number can combine, ordered by combination index. Minimum group number 1, upper limit unknown. Index range 0-4, supports up to 5-unit combination. The base unit additionally requires configuring the core unit and combination count.
  - Equipment Swap: Only two in-game swap systems exist (V2 Gundam and Huckebein MK-III). Do not modify arbitrarily.
  - Terrain: Consists of type and adaptation. Type determines whether the unit can deploy on a given map. Adaptation affects movement and various calculations.
  - Special Abilities: Includes both visible and hidden abilities. Simply check the box. Untested whether selecting too many causes crashes.
  - Cross-Ride System: When enabled, pilots who have also checked the corresponding system can cross-ride this unit.
  - BGM: Select the BGM that plays during unit combat. Some BGMs have multiple versions or are hidden tracks that do not appear in the music player.
- **Unit > Weapon > Weapon Name, Type, Attack Power, Attributes, Hit Rate, Critical Rate, Cost, Requirements, Upgrade Type, Upgrade Bonus, Map Weapon Attributes, Terrain Adaptation** — All editable.
  - Type: Switch between Melee / Ranged.
  - Attributes: Includes P (post-movement) capability, beam weapon flag, deflectable flag, etc. Guided weapons include bits and funnels. Separation is used exclusively for the V Gundam series' BOTTOM ATTACK. Assault is a guessed designation used only for the V Gundam's Wings of Light. Water weapons cannot attack ground targets.
  - Requirements: Includes Will (気力) and skill level requirements. Skill levels range from 0-3, higher levels not defined.
  - Upgrade Type: Corresponds to one of four upgrade configurations in Parameter Editing (not yet implemented), including attack power scaling and cost.
  - Upgrade Bonus: Select one of this unit's weapons as a hidden bonus weapon for max upgrade. To un-hide the target weapon, simply deselect it here.
  - Map Weapon: Three types — Directional, Self-centered, Target-centered. When selecting any type, you can choose the map weapon's visual effect. Some effects are story-specific and have no weapon assigned — the editor limits the range to prevent crashes.
    - Directional: Range in weapon attributes is display-only. Actual damage area is determined by the selectable map weapon range on the right. Detonating cable has a custom area and is shown as an example only.
    - Self-centered: Damage radius determined by the weapon's long range value.
    - Target-centered: Long range value determines the detonation center distance. Damage radius is set by the radius value. Center point is 1, minimum meaningful value is 2.
  - Terrain Adaptation: Weapon-specific terrain adaptation.
- **Pilot > Pilot Name, Full Name, Stats, Personality, Double-Action Level, Initial SP, Will Group, Spirit Commands, Special Skills, Cross-Ride System, Level-up Skills, Terrain Adaptation** — All editable.
  - Will Group: Pilots sharing the same value form a Will group. Being near each other provides a hidden Will bonus.
  - Spirit Commands: Edit which spirits are available and at what level they are learned.
  - Special Skills: Non-levelable pilot skills, including some hidden ones. Prince/Princess — purpose unknown. Ace/Double Action directly light up icons on the pilot screen. Main Character marks all protagonist characters. AI marks all grunt and artificial boss units — function unknown.
  - Cross-Ride System: Same as Unit cross-ride. When enabled, the pilot can cross-ride units that also have the same option checked.
  - Level-up Skills: Define levelable skills (Newtype, Aura Battler, etc.) and at which level they are learned.
  - Terrain: Same as described above.
- **Message > Edit all dialogue text used within battle maps, including stage victory/failure conditions, in-map choice prompts, and character dialogue.
  - The right panel provides simple search/filter functionality, hex index navigation, and filtering by speaker to show only their lines.

---

## Donation

This project has been ongoing for nearly five years. The previous version was written and then scrapped — mainly because refactoring became a nightmare as the project grew, and my skills at the time weren't up to the task. That's been a lingering regret.

Restarting five years later was made possible entirely by VIBE CODING, combined with improved skills. Finally, I can write this editor piece by piece. Of course, this isn't the final version yet — various editing features are being gradually added.

If this editor helps you, feel free to scan the QR code below to help fund my AI subscription. Donations are unconditional, come with no extra features, no promises — purely support and encouragement.

</br>

<!-- markdownlint-disable-next-line MD033 -->
<img src="res/img/bill.png" width="400" alt="QR code">

---

## License

This project is provided for learning and research purposes only. Please ensure you own a legitimate copy of Super Robot Wars α before using this software.
