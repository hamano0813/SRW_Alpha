from typing import cast

from PySide6.QtCore import QEventLoop, QSize, QTimer, QTranslator
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qfluentwidgets import (
    FluentWindow,
    NavigationItemPosition,
    SplashScreen,
    fontStyleSheet,
    getFont,
    setCustomStyleSheet,
)

import config
from gui import OptionFrame

from .custom import CustomIcon


class MainWindow(FluentWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.splash = SplashScreen(CustomIcon.SPLASH.icon(), self)
        self.splash.setIconSize(QSize(960, 720))

        self.init_ui()
        self.splash.finish()

        self.setResizeEnabled(True)

    def init_ui(self):
        loop = QEventLoop(self)
        QTimer.singleShot(3000, loop.quit)

        self.resize(960, 720)
        self.setResizeEnabled(False)
        self.init_icon()
        self.init_pos()
        self.show()

        self.navigationInterface.setExpandWidth(150)
        self.navigationInterface.setReturnButtonVisible(False)

        self.option_frame = OptionFrame(self)

        self.addSubInterface(self.option_frame, CustomIcon.OPTION, self.tr("Options"), position=NavigationItemPosition.BOTTOM)

        self.translateUI()

        loop.exec()

    def init_icon(self):
        self.setWindowIcon(QIcon(":/icon.png"))
        self.titleBar.iconLabel.setFixedSize(108, 36)  # type: ignore
        self.titleBar.iconLabel.setPixmap(CustomIcon.LOGO.icon().pixmap(108, 36))  # type: ignore
        self.titleBar.titleLabel.setStyleSheet("QLabel{font-size: 16px; font-weight: bold;}")  # type: ignore

    def init_pos(self):
        desktop = QApplication.primaryScreen().size()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def resetUI(self):
        config.reset_language()
        if app := QApplication.instance():
            app = cast(QApplication, app)
            style = app.style()
            for widget in app.allWidgets():
                setCustomStyleSheet(widget, fontStyleSheet(getFont()), fontStyleSheet(getFont()))
                style.unpolish(widget)
                style.polish(widget)
                # print(widget)
        self.navigationInterface
        self.option_frame.resetUI()
        for panel_item in self.navigationInterface.panel.items.values():
            panel_item.widget.itemWidget.setFont(getFont())  # type: ignore

    def translateUI(self):
        lang = config.option.get(config.option.language)
        if lang != "en_US":
            translater = QTranslator()
            translater.load(f":/i18n/{lang}.qm")
            QApplication.instance().installTranslator(translater)  # type: ignore
        else:
            QApplication.instance().removeTranslator(QTranslator())  # type: ignore

        self.setWindowTitle(self.tr("Super Robot Wars α Rom Editor") + " - v0.1.0")
        self.translate_frame("OptionFrame", "Options")
        self.option_frame.translateUI()

    def translate_frame(self, frame: str, title: str):
        self.navigationInterface.panel.items[frame].widget.itemWidget.setText(self.tr(title))  # type: ignore
