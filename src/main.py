"""
Super Robot Wars α Rom Editor 主程序入口
"""

import os
import sys

from PySide6.QtWidgets import QApplication

import config
from gui.main_window import MainWindow

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(__file__))


def scale_dpi():
    """配置DPI缩放设置"""
    # 禁用Qt自动缩放，使用自定义缩放因子
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
