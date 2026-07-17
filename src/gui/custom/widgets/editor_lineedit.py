"""
表格编辑器专用 QLineEdit — 纯文字绘制，无边框/无焦点横线

继承链：
    EditorLineEdit     — 基类（透明背景 + 四角圆角）
    FirstColLineEdit   — 首列（左圆右直）
    MidColLineEdit     — 中间列（四角直角）
    LastColLineEdit    — 末列（左直右圆）

Classes:
    EditorLineEdit: 表格编辑器基类
    FirstColLineEdit: 首列专用编辑器
    MidColLineEdit: 中间列专用编辑器
    LastColLineEdit: 末列专用编辑器
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLineEdit
from qfluentwidgets import isDarkTheme


class EditorLineEdit(QLineEdit):
    """表格编辑器基类 — 透明背景 + 纯文字绘制

    无边框、无焦点指示线，仅通过 palette 控制文字颜色。
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFrame(False)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)

    # ========== 主题色 ==========

    def _text_color(self) -> QColor:
        """文字颜色"""
        return QColor(255, 255, 255) if isDarkTheme() else QColor(0, 0, 0)

    # ========== 绘制 ==========

    def paintEvent(self, e):
        """仅设置文字颜色，由 QLineEdit 完成透明背景绘制"""
        palette = self.palette()
        palette.setColor(palette.ColorRole.Text, self._text_color())
        self.setPalette(palette)
        QLineEdit.paintEvent(self, e)


class FirstColLineEdit(EditorLineEdit):
    """首列编辑器 — 左圆右直"""

    def focusInEvent(self, e):
        """获得焦点时光标定位到末尾，不选中全文"""
        super().focusInEvent(e)
        self.setCursorPosition(len(self.text()))

    def paintEvent(self, e):
        """仅设置文字颜色，形状由表格 delegate 的背景圆角决定"""
        palette = self.palette()
        palette.setColor(palette.ColorRole.Text, self._text_color())
        self.setPalette(palette)
        QLineEdit.paintEvent(self, e)


class LastColLineEdit(EditorLineEdit):
    """末列编辑器 — 左直右圆"""

    def focusInEvent(self, e):
        """获得焦点时光标定位到末尾，不选中全文"""
        super().focusInEvent(e)
        self.setCursorPosition(len(self.text()))

    def paintEvent(self, e):
        """仅设置文字颜色，形状由表格 delegate 的背景圆角决定"""
        palette = self.palette()
        palette.setColor(palette.ColorRole.Text, self._text_color())
        self.setPalette(palette)
        QLineEdit.paintEvent(self, e)


class MidColLineEdit(EditorLineEdit):
    """中间列编辑器 — 四角直角"""

    def focusInEvent(self, e):
        """获得焦点时光标定位到末尾，不选中全文"""
        super().focusInEvent(e)
        self.setCursorPosition(len(self.text()))

    def paintEvent(self, e):
        """仅设置文字颜色，形状由表格 delegate 的背景圆角决定"""
        palette = self.palette()
        palette.setColor(palette.ColorRole.Text, self._text_color())
        self.setPalette(palette)
        QLineEdit.paintEvent(self, e)
