import os
import sys

from PySide6.QtWidgets import QApplication

import config
from gui.main_window import MainWindow

sys.path.append(os.path.dirname(__file__))


def scale_dpi():
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(config.option.get(config.option.dpi))


def main():
    scale_dpi()
    app = QApplication(sys.argv)
    MainWindow()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
