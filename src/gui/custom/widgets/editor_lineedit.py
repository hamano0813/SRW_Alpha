"""
表格编辑器专用 QLineEdit — 纯自绘，不依赖 qfluentwidgets QSS

继承链：
    EditorLineEdit     — V1：表格通用编辑器（四角圆角）
    FirstColLineEdit   — V2：首列专用（左圆右直 + 焦点横线左圆右直）
    LastColLineEdit    — V3：末列专用（左直右圆 + 焦点横线左直右圆）

Classes:
    EditorLineEdit: 表格编辑器基类
    FirstColLineEdit: 首列专用编辑器
    LastColLineEdit: 末列专用编辑器
"""

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QColor, QPainter, QPainterPath
from PySide6.QtWidgets import QLineEdit
from qfluentwidgets import isDarkTheme, themeColor


class EditorLineEdit(QLineEdit):
    """表格编辑器基类 — 纯 QLineEdit + 自绘背景/边框/焦点指示线

    不依赖 FluentStyleSheet，所有视觉效果由 paintEvent 控制。
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # 去掉默认边框和背景
        self.setFrame(False)
        self.setAttribute(Qt.WA_MacShowFocusRect, False)

        # 样式常量
        self._radius = 5
        self._border_width = 1

    # ========== 主题色 ==========

    def _focus_border_color(self) -> QColor:
        """焦点边框/指示线颜色"""
        return themeColor()

    def _text_color(self) -> QColor:
        """文字颜色"""
        return QColor(255, 255, 255) if isDarkTheme() else QColor(0, 0, 0)

    # ========== 绘制 ==========

    def paintEvent(self, e):
        """透明背景文字 + 焦点横线覆盖"""
        palette = self.palette()
        palette.setColor(palette.ColorRole.Text, self._text_color())
        self.setPalette(palette)
        QLineEdit.paintEvent(self, e)

        if self.hasFocus():
            self._draw_focus_bar(None)

    def _draw_focus_bar(self, painter=None):
        """绘制底部焦点指示横线（四角圆角）"""
        r = self._radius
        bw = self._border_width
        w = self.width()
        h = self.height()
        x = 0

        # 底部 10px 高区域
        bar_bottom = h - bw
        bar_top = bar_bottom - 10

        path = QPainterPath()
        path.addRoundedRect(QRectF(x, bar_top, w, 10), r, r)

        inner = QPainterPath()
        inner.addRect(QRectF(x, bar_top, w, 8))
        path = path.subtracted(inner)

        if painter is None:
            painter = QPainter(self)
            painter.setRenderHints(QPainter.Antialiasing)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.fillPath(path, self._focus_border_color())
            painter.end()
        else:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.fillPath(path, self._focus_border_color())


class FirstColLineEdit(EditorLineEdit):
    """首列编辑器 — 左圆右直

    框体左侧 5px 圆角、右侧直角。
    焦点指示线左侧圆角、右侧直角。
    """

    def focusInEvent(self, e):
        """获得焦点时光标定位到末尾，不选中全文"""
        super().focusInEvent(e)
        self.setCursorPosition(len(self.text()))

    def paintEvent(self, e):
        """透明背景文字 + 左圆右直焦点横线"""
        palette = self.palette()
        palette.setColor(palette.ColorRole.Text, self._text_color())
        self.setPalette(palette)
        QLineEdit.paintEvent(self, e)

        if self.hasFocus():
            self._draw_focus_bar_first_col()

    @staticmethod
    def _left_round_path(rect: QRectF, r: float) -> QPainterPath:
        """构建左圆右直的矩形路径"""
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        path = QPainterPath()
        # 从右上开始顺时针
        path.moveTo(x + w, y)  # 右上（直角）
        path.lineTo(x + r, y)  # 上边 → 左上弧
        path.quadTo(x, y, x, y + r)  # 左上圆角
        path.lineTo(x, y + h - r)  # 左边
        path.quadTo(x, y + h, x + r, y + h)  # 左下圆角
        path.lineTo(x + w, y + h)  # 底边（直角）
        path.lineTo(x + w, y)  # 右边（直角）
        path.closeSubpath()
        return path

    def _draw_focus_bar_first_col(self):
        """绘制底部焦点指示横线（左圆右直）"""
        r = self._radius
        bw = self._border_width
        w = self.width()
        h = self.height()
        x = 0

        bar_bottom = h - bw
        bar_top = bar_bottom - 10

        # 左圆 + 中间矩形 + 右直角
        left = QPainterPath()
        left.addRoundedRect(QRectF(x, bar_top, 10, 10), r, r)
        mid = QPainterPath()
        mid.addRect(QRectF(x + 5, bar_top, w - 10, 10))
        right = QPainterPath()
        right.addRect(QRectF(x + w - 10, bar_top, 10, 10))

        bar = left.united(mid).united(right)

        # 减去上部 8px，保留底部 2px
        inner = QPainterPath()
        inner.addRect(QRectF(x, bar_top, w, 8))
        bar = bar.subtracted(inner)

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillPath(bar, self._focus_border_color())
        painter.end()


class LastColLineEdit(EditorLineEdit):
    """末列编辑器 — 左直右圆

    框体左侧直角、右侧 5px 圆角。
    焦点指示线左侧直角、右侧圆角。
    """

    def focusInEvent(self, e):
        """获得焦点时光标定位到末尾，不选中全文"""
        super().focusInEvent(e)
        self.setCursorPosition(len(self.text()))

    def paintEvent(self, e):
        """透明背景文字 + 左直右圆焦点横线"""
        palette = self.palette()
        palette.setColor(palette.ColorRole.Text, self._text_color())
        self.setPalette(palette)
        QLineEdit.paintEvent(self, e)

        if self.hasFocus():
            self._draw_focus_bar_last_col()

    @staticmethod
    def _right_round_path(rect: QRectF, r: float) -> QPainterPath:
        """构建左直右圆的矩形路径"""
        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
        path = QPainterPath()
        # 从左上开始顺时针
        path.moveTo(x, y)  # 左上（直角）
        path.lineTo(x + w - r, y)  # 上边 → 右上弧
        path.quadTo(x + w, y, x + w, y + r)  # 右上圆角
        path.lineTo(x + w, y + h - r)  # 右边
        path.quadTo(x + w, y + h, x + w - r, y + h)  # 右下圆角
        path.lineTo(x, y + h)  # 底边（直角）
        path.lineTo(x, y)  # 左边（直角）
        path.closeSubpath()
        return path

    def _draw_focus_bar_last_col(self):
        """绘制底部焦点指示横线（左直右圆）"""
        r = self._radius
        bw = self._border_width
        w = self.width()
        h = self.height()
        x = 0

        bar_bottom = h - bw
        bar_top = bar_bottom - 10

        # 左直角 + 中间矩形 + 右圆
        left = QPainterPath()
        left.addRect(QRectF(x, bar_top, 10, 10))
        mid = QPainterPath()
        mid.addRect(QRectF(x + 5, bar_top, w - 10, 10))
        right = QPainterPath()
        right.addRoundedRect(QRectF(x + w - 10, bar_top, 10, 10), r, r)

        bar = left.united(mid).united(right)

        # 减去上部 8px，保留底部 2px
        inner = QPainterPath()
        inner.addRect(QRectF(x, bar_top, w, 8))
        bar = bar.subtracted(inner)

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.fillPath(bar, self._focus_border_color())
        painter.end()
