"""
垂直微调框组件 - 使用 FluentIcon 箭头按钮

提供 SpinArrowButton（单个方向箭头）和 VerticalSpinBox（右置上下按钮微调框）。
VerticalSpinBox 的 editable 参数控制是否允许键盘输入。

Classes:
    SpinArrowButton: 单个方向箭头按钮
    VerticalSpinBox: 垂直微调框，无 flyout
"""

from PySide6.QtCore import QEvent, QRectF, Qt
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QSpinBox, QToolButton, QVBoxLayout, QWidget
from qfluentwidgets import FluentIcon, isDarkTheme, setFont
from qfluentwidgets.components.widgets.spin_box import SpinBoxBase


class SpinArrowButton(QToolButton):
    """单个方向箭头按钮 - 使用 FluentIcon ARROW_DOWN

    上箭头通过旋转 180° 实现，颜色规则与 ComboBox 一致。
    """

    def __init__(self, up: bool, parent=None):
        """初始化方向箭头按钮

        Args:
            up: True 为上箭头（递增），False 为下箭头（递减）
            parent: 父 QWidget
        """
        super().__init__(parent=parent)
        self._up = up
        self._hovered = False
        self.setFixedSize(26, 16)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def enterEvent(self, e):
        """鼠标进入时标记悬停状态并刷新"""
        self._hovered = True
        self.update()
        super().enterEvent(e)

    def leaveEvent(self, e):
        """鼠标离开时清除悬停状态并刷新"""
        self._hovered = False
        self.update()
        super().leaveEvent(e)

    def paintEvent(self, e):
        """自绘箭头图标，根据悬停/按下/禁用状态调整透明度"""
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        if not self.isEnabled():
            painter.setOpacity(0.36)
        elif self.isDown():
            painter.setOpacity(0.7)
        elif self._hovered:
            painter.setOpacity(0.8)

        s = 9
        x = (self.width() - s) / 2 - 4
        y = (self.height() - s) / 2
        if self._up:
            y += 2
        else:
            y -= 2

        if self._up:
            painter.save()
            painter.translate(x + s / 2, y + s / 2)
            painter.rotate(180)
            if isDarkTheme():
                FluentIcon.ARROW_DOWN.render(painter, QRectF(-s / 2, -s / 2, s, s))
            else:
                FluentIcon.ARROW_DOWN.render(painter, QRectF(-s / 2, -s / 2, s, s), fill="#646464")
            painter.restore()
        else:
            if isDarkTheme():
                FluentIcon.ARROW_DOWN.render(painter, QRectF(x, y, s, s))
            else:
                FluentIcon.ARROW_DOWN.render(painter, QRectF(x, y, s, s), fill="#646464")


class VerticalSpinBox(SpinBoxBase, QSpinBox):
    """垂直微调框 - 右置上下箭头按钮直接步进，无 flyout

    Args:
        parent: 父 QWidget
        editable: 是否允许键盘输入（默认 True）。False 时禁用输入框和文字选中。
    """

    def __init__(self, parent=None, editable=True):
        """初始化垂直微调框

        Args:
            parent: 父 QWidget
            editable: 是否允许键盘输入（默认 True）。False 时禁用输入框和文字选中。
        """
        super().__init__(parent)
        self._editable = editable
        self.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lineEdit().setTextMargins(0, 0, 26, 0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # 禁用 SpinBoxBase 的右键菜单
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        # ========== 右侧垂直按钮面板 ==========

        panel = QWidget(self)
        panel.setFixedWidth(26)
        vbox = QVBoxLayout(panel)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        self._up_btn = SpinArrowButton(up=True)
        self._dn_btn = SpinArrowButton(up=False)
        vbox.addWidget(self._up_btn)
        vbox.addWidget(self._dn_btn)

        self.hBoxLayout.addWidget(panel, 0, Qt.AlignmentFlag.AlignRight)
        self.hBoxLayout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        self._up_btn.clicked.connect(self.stepUp)
        self._dn_btn.clicked.connect(self.stepDown)

        # ========== 非编辑模式 ==========

        if not editable:
            le = self.lineEdit()
            le.setReadOnly(True)
            le.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            le.setCursor(Qt.CursorShape.ArrowCursor)
            le.installEventFilter(self)

    def eventFilter(self, obj, e):
        """监听 lineedit 事件 + 窗口鼠标点击交出焦点"""
        # 非编辑模式下拦截 lineedit 的鼠标事件
        if obj == self.lineEdit() and not self._editable:
            t = e.type()
            if t in (QEvent.Type.MouseButtonPress, QEvent.Type.MouseButtonRelease, QEvent.Type.MouseButtonDblClick, QEvent.Type.MouseMove):
                return True
        # 窗口级鼠标点击 — 点击到 spin 范围外则交出焦点
        if e.type() == QEvent.Type.MouseButtonPress and self.hasFocus():
            pos = e.globalPosition().toPoint() if hasattr(e, 'globalPosition') else e.globalPos()
            if not self.rect().contains(self.mapFromGlobal(pos)):
                self.clearFocus()
                return False
        return super().eventFilter(obj, e)

    def focusInEvent(self, e):
        """获得焦点时监听父窗口鼠标事件"""
        super().focusInEvent(e)
        if w := self.window():
            w.installEventFilter(self)

    def focusOutEvent(self, e):
        """失去焦点时移除父窗口事件监听"""
        if w := self.window():
            w.removeEventFilter(self)
        super().focusOutEvent(e)

    def setSymbolVisible(self, isVisible: bool):
        """显示/隐藏步进箭头

        Args:
            isVisible: True 显示上下箭头，False 隐藏
        """
        super().setSymbolVisible(isVisible)
        self._up_btn.setVisible(isVisible)
        self._dn_btn.setVisible(isVisible)

    def resetUI(self):
        """从全局配置刷新字体"""
        setFont(self)
        setFont(self.lineEdit())
