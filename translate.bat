uv run pyside6-lupdate ^
    src/gui/main_window.py ^
    src/gui/home/home_frame.py ^
    src/gui/home/file_table.py ^
    src/gui/option/option_frame.py ^
    src/gui/option/color_card.py ^
    src/gui/option/rom_card.py ^
    src/gui/option/font_card.py ^
    src/gui/custom/enums.py ^
    src/gui/custom/fields.py ^
-ts ^
    res/i18n/zh_CN.ts ^
    res/i18n/ja_JP.ts

uv run pyside6-linguist res/i18n/zh_CN.ts
uv run pyside6-lrelease res/i18n/zh_CN.ts -qm res/i18n/zh_CN.qm

uv run pyside6-linguist res/i18n/ja_JP.ts
uv run pyside6-lrelease res/i18n/ja_JP.ts -qm res/i18n/ja_JP.qm