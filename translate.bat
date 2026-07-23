uv run pyside6-lupdate ^
    src/gui/main_window.py ^
    src/gui/interface/home/home_frame.py ^
    src/gui/interface/unit/unit_frame.py ^
    src/gui/interface/unit/cards/transform.py ^
    src/gui/interface/unit/cards/terrain.py ^
    src/gui/interface/unit/cards/abilities.py ^
    src/gui/interface/unit/cards/series.py ^
    src/gui/interface/unit/cards/bgm.py ^
    src/gui/interface/unit/cards/weapon_attr.py ^
    src/gui/interface/unit/cards/weapon_map.py ^
    src/gui/interface/unit/cards/weapon_adapt.py ^
    src/gui/interface/unit/weapon_list.py ^
    src/gui/interface/pilot/pilot_table.py ^
    src/gui/interface/pilot/pilot_panel.py ^
    src/gui/interface/snmsg/msg_frame.py ^
    src/gui/interface/snmsg/msg_panel.py ^
    src/gui/interface/option/option_frame.py ^
    src/gui/interface/option/color_card.py ^
    src/gui/interface/option/rom_card.py ^
    src/gui/interface/option/font_card.py ^
    src/gui/custom/enums.py ^
    src/gui/custom/fields.py ^
-ts ^
    res/i18n/zh_CN.ts ^
    res/i18n/ja_JP.ts

uv run pyside6-linguist res/i18n/zh_CN.ts
uv run pyside6-lrelease res/i18n/zh_CN.ts -qm res/i18n/zh_CN.qm

uv run pyside6-linguist res/i18n/ja_JP.ts
uv run pyside6-lrelease res/i18n/ja_JP.ts -qm res/i18n/ja_JP.qm

uv run pyside6-rcc  .\res\res.qrc -o .\src\res.py
