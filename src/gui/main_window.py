"""
主窗口模块 - 基于FluentWindow的现代化UI界面
"""

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
from gui import HomeFrame, OptionFrame

from .custom import CustomIcon


class MainWindow(FluentWindow):
    """主窗口类 - 继承自FluentWindow"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 创建启动画面
        self.splash = SplashScreen(CustomIcon.SPLASH.icon(), self)
        self.splash.setIconSize(QSize(960, 720))

        self.init_ui()

        self.splash.finish()
        self.setResizeEnabled(True)

    def init_ui(self):
        """初始化用户界面"""
        # 创建事件循环控制启动画面显示时间
        loop = QEventLoop(self)
        QTimer.singleShot(3000, loop.quit)  # 3秒后自动关闭

        self.resize(960, 720)
        self.setResizeEnabled(False)  # 初始化阶段禁用窗口大小调整
        self.init_icon()
        self.init_pos()
        self.show()

        # 配置导航栏样式
        self.navigationInterface.setExpandWidth(150)  # 设置侧边栏展开宽度
        self.navigationInterface.setReturnButtonVisible(False)  # 隐藏返回按钮

        # 创建主页并添加到导航栏
        self.home_frame = HomeFrame(self)
        self.addSubInterface(self.home_frame, CustomIcon.HOME, self.tr("Home"))

        # 创建选项设置页面并添加到导航栏底部
        self.option_frame = OptionFrame(self)
        self.addSubInterface(self.option_frame, CustomIcon.OPTION, self.tr("Options"), position=NavigationItemPosition.BOTTOM)

        self.translateUI()

        # 执行事件循环，保持启动画面显示直到定时器结束
        loop.exec()

    def init_icon(self):
        """初始化窗口图标和标题栏"""
        self.setWindowIcon(QIcon(":/icon.png"))  # 设置任务栏和窗口图标
        # 自定义标题栏Logo显示
        self.titleBar.iconLabel.setFixedSize(108, 36)  # type: ignore
        self.titleBar.iconLabel.setPixmap(CustomIcon.LOGO.icon().pixmap(108, 36))  # type: ignore
        # 设置标题栏文字样式
        self.titleBar.titleLabel.setStyleSheet("QLabel{font-size: 16px; font-weight: bold;}")  # type: ignore

    def init_pos(self):
        """初始化窗口位置 - 居中显示"""
        desktop = QApplication.primaryScreen().size()
        w, h = desktop.width(), desktop.height()
        # 计算屏幕中心位置并移动窗口
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def resetUI(self):
        """重置用户界面 - 更新语言和样式"""
        config.reset_language()

        # 获取应用实例并刷新所有组件样式
        if app := QApplication.instance():
            app = cast(QApplication, app)
            style = app.style()
            # 遍历所有组件重新应用字体样式
            for widget in app.allWidgets():
                setCustomStyleSheet(widget, fontStyleSheet(getFont()), fontStyleSheet(getFont()))
                style.unpolish(widget)  # 移除旧样式
                style.polish(widget)  # 应用新样式

        self.navigationInterface
        self.home_frame.resetUI()
        self.option_frame.resetUI()

        # 更新导航栏所有项目的字体
        for panel_item in self.navigationInterface.panel.items.values():
            panel_item.widget.itemWidget.setFont(getFont())  # type: ignore

    def translateUI(self):
        """翻译用户界面 - 加载语言文件"""
        lang = config.option.get(config.option.language)

        # 根据语言设置加载对应的翻译文件
        if lang != "en_US":
            translater = QTranslator()
            translater.load(f":/i18n/{lang}.qm")  # 从资源文件加载翻译
            QApplication.instance().installTranslator(translater)  # type: ignore
        else:
            # 英语环境直接移除翻译器
            QApplication.instance().removeTranslator(QTranslator())  # type: ignore

        # 更新窗口标题和界面文本
        self.setWindowTitle(self.tr("Super Robot Wars α ROM Editor") + " - v0.1.0")
        self.translate_frame("EditorFrame", "Home")
        self.translate_frame("OptionFrame", "Options")
        self.home_frame.translateUI()
        self.option_frame.translateUI()

    def translate_frame(self, frame: str, title: str):
        """翻译导航栏框架标题"""
        # 通过框架名称找到对应的导航项并更新文本
        self.navigationInterface.panel.items[frame].widget.itemWidget.setText(self.tr(title))  # type: ignore
