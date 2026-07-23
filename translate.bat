uv run pyside6-lupdate ^
    -no-obsolete ^
    -extensions py ^
    src/gui ^
    -ts ^
    res/i18n/zh_CN.ts ^
    res/i18n/ja_JP.ts

uv run pyside6-linguist res/i18n/zh_CN.ts
uv run pyside6-lrelease res/i18n/zh_CN.ts -qm res/i18n/zh_CN.qm

uv run pyside6-linguist res/i18n/ja_JP.ts
uv run pyside6-lrelease res/i18n/ja_JP.ts -qm res/i18n/ja_JP.qm

uv run pyside6-rcc  .\res\res.qrc -o .\src\res.py
