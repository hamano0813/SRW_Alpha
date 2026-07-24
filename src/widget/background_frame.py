#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QFrame, QMessageBox

from widget.abstract_widget import BackgroundWidget


class BackgroundFrame(BackgroundWidget, QFrame):
    def __init__(self, parent, **kwargs):
        QFrame.__init__(self, parent, Qt.Widget)
        BackgroundWidget.__init__(self, **kwargs)
        self.original_data = None

    def set_roms(self, roms: list):
        pass

    def parse(self):
        pass

    def build(self):
        pass

    def builded(self) -> bool:
        pass

    def closeEvent(self, event: QCloseEvent) -> None:
        if not self.builded():
            box = QMessageBox(QMessageBox.Question, '', '是否写入修改？', parent=self, flags=Qt.FramelessWindowHint)
            accept = box.addButton('写入', QMessageBox.AcceptRole)
            box.addButton('放弃', QMessageBox.RejectRole)
            box.exec()
            if box.clickedButton() == accept:
                self.build()
        event.accept()
