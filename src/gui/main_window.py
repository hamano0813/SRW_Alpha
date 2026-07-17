"""
主窗口模块

基于 FluentWindow 的现代化主界面，管理导航栏、主页和设置页的切换。
提供启动画面、界面语言切换、全局样式刷新等功能。

Classes:
    MainWindow: 主窗口类，继承自 FluentWindow
"""

import random
from typing import cast

from PySide6.QtCore import QEventLoop, QSize, Qt, QTimer, QTranslator
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication
from qfluentwidgets import (
    FluentTitleBar,
    FluentWindow,
    NavigationItemPosition,
    SplashScreen,
    fontStyleSheet,
    getFont,
    setCustomStyleSheet,
)

import config
import utils
from core.rom import Rom
from gui import HomeFrame, OptionFrame, RobotFrame
from gui.custom.fields import FieldMapping

from .custom import CustomIcon


class MainWindow(FluentWindow):
    """主窗口类 - 集成导航栏、启动画面和界面刷新"""

    _SIZE = utils.best_resolution()

    def __init__(self, parent=None):
        super().__init__(parent)
        splash_idx = random.randrange(1, 5)
        self.splash = SplashScreen(
            QIcon(QPixmap(f":/splash/splash{splash_idx}.png").scaled(*self._SIZE, mode=Qt.TransformationMode.SmoothTransformation)), self
        )
        self.splash.setIconSize(QSize(*self._SIZE))

        self.init_core()
        self.init_ui()

        self.home_frame.parseClicked.connect(self.parse_data)
        self.home_frame.buildClicked.connect(self.build_data)

        self.splash.finish()
        self.setResizeEnabled(True)

    def init_core(self):
        self._rom = Rom()
        self._field = FieldMapping()

    def init_ui(self):
        """初始化界面：启动画面 → 注册导航页 → 加载语言"""
        loop = QEventLoop(self)
        QTimer.singleShot(3000, loop.quit)

        self.resize(*self._SIZE)
        self.setResizeEnabled(False)
        self.init_icon()
        self.init_pos()
        self.show()

        self.navigationInterface.setExpandWidth(150)
        self.navigationInterface.setReturnButtonVisible(False)

        self.home_frame = HomeFrame(self)
        self.addSubInterface(self.home_frame, CustomIcon.HOME, self.tr("Home"))

        self.robot_frame = RobotFrame(self._field, self)
        self.addSubInterface(self.robot_frame, CustomIcon.HELP, self.tr("Robot"))

        self.option_frame = OptionFrame(self)
        self.addSubInterface(self.option_frame, CustomIcon.OPTION, self.tr("Options"), position=NavigationItemPosition.BOTTOM)

        self.option_frame.themeChanged.connect(self.resetUI)

        self.translateUI()
        self.resetUI()

        loop.exec()

    def init_icon(self):
        """设置窗口图标和标题栏样式"""
        self.setWindowIcon(QIcon(":/icon.png"))
        titleBar = cast(FluentTitleBar, self.titleBar)
        titleBar.iconLabel.setFixedSize(100, 36)
        titleBar.iconLabel.setPixmap(QPixmap(":/logo.png").scaled(100, 36, mode=Qt.TransformationMode.SmoothTransformation))
        titleBar.titleLabel.setStyleSheet("QLabel{font-size: 16px; font-weight: bold;}")

    def init_pos(self):
        """初始化窗口位置为屏幕居中"""
        desktop = QApplication.primaryScreen().size()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def resetUI(self):
        """重置界面：切换语言后刷新所有组件的字体和样式"""
        config.reset_language()

        if app := QApplication.instance():
            app = cast(QApplication, app)
            style = app.style()
            for widget in app.allWidgets():
                setCustomStyleSheet(widget, fontStyleSheet(getFont()), fontStyleSheet(getFont()))
                style.unpolish(widget)
                style.polish(widget)

        self.home_frame.resetUI()
        self.robot_frame.resetUI()
        self.option_frame.resetUI()

        for panel_item in self.navigationInterface.panel.items.values():
            panel_item.widget.itemWidget.setFont(getFont())  # type: ignore

    def translateUI(self):
        """刷新界面语言：加载 .qm 翻译文件并更新所有导航文本"""
        lang = config.option.get(config.option.language)

        if lang != "en_US":
            translater = QTranslator()
            translater.load(f":/i18n/{lang}.qm")
            QApplication.instance().installTranslator(translater)  # type: ignore
        else:
            QApplication.instance().removeTranslator(QTranslator())  # type: ignore

        self._field.translateUI()

        self.setWindowTitle(self.tr("Super Robot Wars α ROM Editor") + " - v0.2.0")
        self.translate_frame("EditorFrame", "Home")
        self.translate_frame("RobotFrame", "Robot")
        self.translate_frame("OptionFrame", "Options")
        self.home_frame.translateUI()
        self.robot_frame.translateUI()
        self.option_frame.translateUI()

    def translate_frame(self, frame: str, title: str):
        """更新导航栏中指定框架的显示标题"""
        self.navigationInterface.panel.items[frame].widget.itemWidget.setText(self.tr(title))  # type: ignore

    def parse_data(self):
        self._rom.parse_cache()
        self.robot_frame.set_rom_data(self._rom.data)

    def build_data(self):
        pass
