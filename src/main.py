"""
Super Robot Wars α ROM Editor 主程序入口

提供DPI缩放配置和应用程序启动入口。
负责在启动时设置高DPI缩放因子，然后创建主窗口进入事件循环。

Classes:
    (无类定义，仅函数入口)
"""

import os
import sys

from PySide6.QtWidgets import QApplication

import config
from gui import MainWindow

sys.path.append(os.path.dirname(__file__))


def scale_dpi():
    """配置DPI缩放设置"""
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(config.option.get(config.option.dpi))


def main():
    """应用程序主入口点"""
    scale_dpi()
    app = QApplication(sys.argv)
    MainWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
