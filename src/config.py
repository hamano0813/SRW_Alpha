"""
配置管理模块

管理应用程序的全局配置，包括UI设置、字体配置、ROM文件路径等。
使用QFluentWidgets的配置系统实现配置的持久化存储。
"""

import os

from qfluentwidgets import (
    ConfigItem,
    OptionsConfigItem,
    OptionsValidator,
    QConfig,
    qconfig,
)

# 获取项目根目录并构建配置文件路径
current_path = os.path.dirname(os.path.dirname(__file__)).replace("\\", "/")
config_path = os.path.join(current_path, "config.json")


class Option(QConfig):
    """应用程序配置选项类"""

    # 界面显示设置
    dpi = OptionsConfigItem(
        "QFluentWidgets", "DPI", 1, OptionsValidator([1, 1.25, 1.5, 1.75, 2]), restart=True
    )  # DPI缩放比例，需要重启生效
    language = OptionsConfigItem("QFluentWidgets", "Language", "en_US", OptionsValidator(["en_US", "zh_CN", "zh_TW", "ja_JP"]))  # 界面语言

    # 各语言字体设置
    en_font = ConfigItem("QFluentWidgets", "ENFont", "Segoe UI")  # 英文字体
    cn_font = ConfigItem("QFluentWidgets", "CNFont", "Microsoft YaHei UI")  # 简体中文字体
    tw_font = ConfigItem("QFluentWidgets", "TWFont", "Microsoft JhengHei UI")  # 繁体中文字体
    jp_font = ConfigItem("QFluentWidgets", "JPFont", "Yu Gothic UI")  # 日文字体

    # ROM文件路径配置
    robot_raf = ConfigItem("Rom", "ROBOT.RAF", "")  # 机体数据文件
    pilot_bin = ConfigItem("Rom", "PILOT.BIN", "")  # 驾驶员数据文件
    snmsg_bin = ConfigItem("Rom", "SNMSG.BIN", "")  # 剧情文本文件
    sndata_bin = ConfigItem("Rom", "SNDATA.BIN", "")  # 剧情数据文件
    enlist_bin = ConfigItem("Rom", "ENLIST.BIN", "")  # 敌方单位列表文件
    aiunp_bin = ConfigItem("Rom", "AIUNP.BIN", "")  # AI数据文件
    script_bin = ConfigItem("Rom", "SCRIPT.BIN", "")  # 剧本数据文件
    prm_grp_bin = ConfigItem("Rom", "PRM_GRP.BIN", "")  # 参数组文件


option = Option()


def reset_language():
    """
    根据当前语言设置重置字体优先级

    设置字体回退顺序，确保不同语言的文本都能正确显示。
    优先使用当前语言的默认字体，然后按需回退到其他语言字体。
    """
    current_language = qconfig.get(option.language)
    # 获取各语言字体配置
    zh_cn = qconfig.get(option.cn_font)
    zh_tw = qconfig.get(option.tw_font)
    ja_jp = qconfig.get(option.jp_font)
    en_us = qconfig.get(option.en_font)

    # 根据当前语言设置字体优先级顺序
    if current_language == "zh_CN":
        families = [zh_cn, ja_jp, en_us]  # 简中优先，日文次之，英文兜底
    elif current_language == "zh_TW":
        families = [zh_tw, ja_jp, en_us]  # 繁中优先，日文次之，英文兜底
    elif current_language == "ja_JP":
        families = [ja_jp, zh_cn, en_us]  # 日文优先，简中次之，英文兜底
    else:
        families = [en_us, ja_jp, zh_cn]  # 英文优先，日文次之，简中兜底

    # 应用字体配置到全局设置
    qconfig.set(qconfig.fontFamilies, families)


# 加载配置文件并初始化语言设置
qconfig.load(config_path, option)
reset_language()
