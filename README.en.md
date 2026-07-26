# SRW Alpha ROM Editor — Super Robot Wars α ROM Editor

[![Python](https://img.shields.io/badge/Python-≥3.14-blue?logo=python&style=flat&labelColor=013243)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.7+-green?logo=qt&style=flat&labelColor=013243)](https://doc.qt.io/qtforpython-6/)
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

Download the latest installer from the [Releases](https://github.com/hamano0813/SRW_Alpha/releases) page. Run the installer and you're ready to go.

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

<img src="res/bill.png" width="400" alt="QR code">

---

## License

This project is provided for learning and research purposes only. Please ensure you own a legitimate copy of Super Robot Wars α before using this software.
