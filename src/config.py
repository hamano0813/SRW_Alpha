"""
配置管理模块

管理应用程序的全局配置，包括UI设置、字体配置、ROM文件路径等。
使用 QFluentWidgets 的配置系统实现配置的持久化存储和热更新。

Classes:
    Option: 应用程序配置选项类，定义所有可持久化的配置项
"""

import os

from qfluentwidgets import (
    BoolValidator,
    ConfigItem,
    FolderValidator,
    OptionsConfigItem,
    OptionsValidator,
    QConfig,
    qconfig,
)

current_path = os.path.dirname(os.path.dirname(__file__)).replace("\\", "/")
config_path = os.path.join(current_path, "config.json")


class Option(QConfig):
    """应用程序全局配置类"""

    # DPI缩放比例（修改后需重启生效）
    dpi = OptionsConfigItem("QFluentWidgets", "DPI", 1, OptionsValidator([1, 1.25, 1.5, 1.75, 2]), restart=True)
    language = OptionsConfigItem("QFluentWidgets", "Language", "en_US", OptionsValidator(["en_US", "zh_CN", "ja_JP"]))

    # 各语言字体设置
    en_font = ConfigItem("QFluentWidgets", "ENFont", "Segoe UI Semibold")
    cn_font = ConfigItem("QFluentWidgets", "CNFont", "Microsoft YaHei UI")
    jp_font = ConfigItem("QFluentWidgets", "JPFont", "Yu Gothic UI Semibold")

    # ROM 文件配置
    source_rom = ConfigItem("Rom", "SourceRom", "")
    target_rom = ConfigItem("Rom", "TargetRom", "")
    cache_dir = ConfigItem("Rom", "CacheDir", "cache", FolderValidator())
    auto_clean = ConfigItem("Rom", "AutoClean", False, BoolValidator())


option = Option()


def reset_language():
    """根据当前语言设置全局字体回退顺序"""
    current_language = qconfig.get(option.language)
    zh_cn = qconfig.get(option.cn_font)
    ja_jp = qconfig.get(option.jp_font)
    en_us = qconfig.get(option.en_font)

    # 当前语言字体优先，关联语言次之，英文兜底
    if current_language == "zh_CN":
        families = [zh_cn, ja_jp, en_us]
    elif current_language == "ja_JP":
        families = [ja_jp, zh_cn, en_us]
    else:
        families = [en_us, ja_jp, zh_cn]

    qconfig.set(qconfig.fontFamilies, families)


qconfig.load(config_path, option)
reset_language()
