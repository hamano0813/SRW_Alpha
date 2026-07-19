"""
代理窗体 - 自动向子控件传播 resetUI / translateUI

继承 QFrame，重写 resetUI() 和 translateUI() 以遍历直接子控件，
调用所有实现了同名方法的子控件。减少外层手动维护传播链。

Classes:
    ProxyFrame: 代理窗体
"""

from PySide6.QtWidgets import QFrame, QWidget


class ProxyFrame(QFrame):
    """代理窗体 - 自动向下传播 resetUI / translateUI

    适用于需要统一刷新界面主题或语言的组合控件，
    无需在每个父容器里手动逐一调用子控件的重置方法。
    """

    def resetUI(self):
        """遍历所有直接子控件，调用实现了 resetUI 的子控件"""
        for child in self.children():
            if isinstance(child, QWidget) and hasattr(child, "resetUI"):
                child.resetUI()  # type: ignore

    def translateUI(self):
        """遍历所有直接子控件，调用实现了 translateUI 的子控件"""
        for child in self.children():
            if isinstance(child, QWidget) and hasattr(child, "translateUI"):
                child.translateUI()  # type: ignore
