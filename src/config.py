import os

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication
from qfluentwidgets import (
    ConfigItem,
    OptionsConfigItem,
    OptionsValidator,
    QConfig,
    qconfig,
)

current_path = os.path.dirname(os.path.dirname(__file__)).replace("\\", "/")
config_path = os.path.join(current_path, "config.json")


class Option(QConfig):
    dpi = OptionsConfigItem("QFluentWidgets", "DPI", 1, OptionsValidator([1, 1.25, 1.5, 1.75, 2]), restart=True)
    language = OptionsConfigItem("QFluentWidgets", "Language", "en_US", OptionsValidator(["en_US", "zh_CN", "zh_TW", "ja_JP"]))

    en_font = ConfigItem("QFluentWidgets", "ENFont", "Segoe UI")
    cn_font = ConfigItem("QFluentWidgets", "CNFont", "Microsoft YaHei UI")
    tw_font = ConfigItem("QFluentWidgets", "TWFont", "Microsoft JhengHei UI")
    jp_font = ConfigItem("QFluentWidgets", "JPFont", "Yu Gothic UI")

    robot_raf = ConfigItem("Rom", "ROBOT.RAF", "")
    pilot_bin = ConfigItem("Rom", "PILOT.BIN", "")
    snmsg_bin = ConfigItem("Rom", "SNMSG.BIN", "")
    sndata_bin = ConfigItem("Rom", "SNDATA.BIN", "")
    enlist_bin = ConfigItem("Rom", "ENLIST.BIN", "")
    aiunp_bin = ConfigItem("Rom", "AIUNP.BIN", "")
    script_bin = ConfigItem("Rom", "SCRIPT.BIN", "")
    prm_grp_bin = ConfigItem("Rom", "PRM_GRP.BIN", "")


option = Option()


def reset_language():
    current_language = qconfig.get(option.language)
    zh_cn = qconfig.get(option.cn_font)
    zh_tw = qconfig.get(option.tw_font)
    ja_jp = qconfig.get(option.jp_font)
    en_us = qconfig.get(option.en_font)
    if current_language == "zh_CN":
        families = [zh_cn, ja_jp, en_us]
    elif current_language == "zh_TW":
        families = [zh_tw, ja_jp, en_us]
    elif current_language == "ja_JP":
        families = [ja_jp, zh_cn, en_us]
    else:
        families = [en_us, ja_jp, zh_cn]

    qconfig.set(qconfig.fontFamilies, families)


qconfig.load(config_path, option)
reset_language()
