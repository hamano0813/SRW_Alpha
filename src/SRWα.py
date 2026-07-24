#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from PySide6.QtWidgets import QApplication

from interface.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
