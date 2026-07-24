"""
数值编辑器 — 继承 SpinBox + CellEditor，左右按钮步进

接受取值范围 (min, max)，左减右加按钮布局，透明背景。
与 CellMappingStepper 实现模式一致，但无映射表。

Classes:
    CellNumberStepper: 数值编辑器
"""

from typing import Any, cast

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath
from PySide6.QtWidgets import QSpinBox, QToolButton
from qfluentwidgets import FluentStyleSheet, isDarkTheme, setCustomStyleSheet
from gui.widget.abstract.spin_box_shim import SpinBox

from .cell_editor import CellEditor


class _ArrowButton(QToolButton):
    """单方向箭头按钮 — 左箭头（递减）或右箭头（递增）"""

    def __init__(self, right: bool, parent=None):
        """初始化箭头按钮

        Args:
            right: True 为右箭头（递增），False 为左箭头（递减）
            parent: 父 QWidget
        """
        super().__init__(parent)
        self._right = right
        self.setFixedSize(24, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, e):
        """根据按钮方向调用 stepUp 或 stepDown

        Args:
            e: 鼠标事件
        """
        parent = cast(CellNumberStepper, self.parent())
        if self._right:
            parent.stepUp()
        else:
            parent.stepDown()

    def paintEvent(self, e):
        """自绘三角形箭头

        Args:
            e: 绘制事件
        """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        color = QColor(200, 200, 200) if isDarkTheme() else QColor(80, 80, 80)
        painter.setBrush(color)

        s = 5
        cx = self.width() / 2
        cy = self.height() / 2

        if self._right:
            path = QPainterPath()
            path.moveTo(QPointF(cx + s, cy))
            path.lineTo(QPointF(cx - s, cy - s))
            path.lineTo(QPointF(cx - s, cy + s))
        else:
            path = QPainterPath()
            path.moveTo(QPointF(cx - s, cy))
            path.lineTo(QPointF(cx + s, cy - s))
            path.lineTo(QPointF(cx + s, cy + s))

        path.closeSubpath()
        painter.drawPath(path)


class CellNumberStepper(SpinBox, CellEditor):
    """数值编辑器 — 左右按钮步进，右对齐

    接受取值范围 (min, max)，在范围内循环。
    禁止键盘手动输入，仅由按钮步进。
    """

    def __init__(self, value_range: tuple[int, int] | None = None, show_sign: bool = False, show_buttons: bool = True, read_only: bool = True, parent=None):
        """初始化数值编辑器

        Args:
            value_range: (最小值, 最大值)，None 表示无限制
            show_sign: 是否强制显示正号
            show_buttons: 是否显示左右微调按钮
            read_only: 文本框是否只读（仅按钮步进），False 时可键盘输入
            parent: 父 QWidget
        """
        self._min: int = 0
        self._max: int = 9999
        if value_range is not None:
            self._min, self._max = value_range

        self._show_sign = show_sign
        self._show_buttons = show_buttons
        self._read_only = read_only if show_buttons else False  # 无按钮时只能靠键盘输入

        QSpinBox.__init__(self, parent)
        CellEditor.__init__(self, parent)

        # 空壳 SpinBox 在 MRO 中 → QSS SpinBox 选择器匹配 → 主题颜色自动生效
        FluentStyleSheet.SPIN_BOX.apply(self)
        setCustomStyleSheet(self,
            "SpinBox { padding: 0px; border: none; border-radius: 0px; background: transparent; }"
            "SpinBox:hover { border: none; background: transparent; }"
            "SpinBox:focus { border: none; background: transparent; }"
            "SpinBox:focus:hover { border: none; background: transparent; }",
            "SpinBox { padding: 0px; border: none; border-radius: 0px; background: transparent; }"
            "SpinBox:hover { border: none; background: transparent; }"
            "SpinBox:focus { border: none; background: transparent; }"
            "SpinBox:focus:hover { border: none; background: transparent; }")

        # ========== 基础样式 ==========

        self.setFrame(False)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.setFixedHeight(28)
        self.setRange(self._min, self._max)

        # ========== 行编辑：透明 ==========

        le = self.lineEdit()
        le.setReadOnly(self._read_only)  # True=仅按钮步进，False=可键盘输入
        le.setFrame(False)
        le.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        # 有按钮时居中（与左右按钮对称），无按钮时右对齐
        if self._show_buttons:
            le.setAlignment(Qt.AlignmentFlag.AlignCenter)
            setCustomStyleSheet(le,
                "background: transparent; border: none; padding-right: 1px; color: #000000;",
                "background: transparent; border: none; padding-right: 1px; color: #FFFFFF;")
        else:
            le.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            setCustomStyleSheet(le,
                "background: transparent; border: none; color: #000000;",
                "background: transparent; border: none; color: #FFFFFF;")
        if self._show_buttons:
            # 按钮模式（只读）：禁止文字选中
            le.selectionChanged.connect(lambda: le.setSelection(0, 0))

        # ========== 左右按钮（手动定位） ==========

        self._btn_left = _ArrowButton(False, self) if self._show_buttons else None
        self._btn_right = _ArrowButton(True, self) if self._show_buttons else None

        # ========== 信号 ==========

        self.valueChanged.connect(self._on_value_changed)

    # ========== 显示格式 ==========

    def textFromValue(self, value: int) -> str:
        """将整数值格式化为显示文本

        show_sign 时正值加 "+" 前缀，与 format_display 保持一致。

        Args:
            value: 整数值

        Returns:
            显示文本
        """
        if self._show_sign and value >= 0:
            return f"+{value}"
        return str(value)

    def focusInEvent(self, e):
        """获得焦点：按钮模式走默认，键盘模式光标移到末尾

        Args:
            e: 焦点事件
        """
        super().focusInEvent(e)
        if not self._show_buttons:
            self.lineEdit().setCursorPosition(len(self.lineEdit().text()))

    # ========== 布局 ==========

    def resizeEvent(self, e):
        """手动定位左右按钮

        Args:
            e: 调整大小事件
        """
        super().resizeEvent(e)
        if self._btn_left and self._btn_right:
            bw = self._btn_left.width()
            y = (self.height() - self._btn_left.height()) // 2
            self._btn_left.move(2, y)
            self._btn_right.move(self.width() - bw - 2, y)

    # ========== CellEditor 数据协议 ==========

    def set_value(self, value) -> None:
        """存入数值并刷新显示

        Args:
            value: 整数
        """
        CellEditor.set_value(self, value)

    def get_value(self) -> int:
        """返回当前数值"""
        return self._value if self._value is not None else 0

    def format_value(self) -> None:
        """将 _value 同步到微调框"""
        self.blockSignals(True)
        if self._value is not None:
            self.setValue(int(self._value))
        self.blockSignals(False)

    def apply_font(self, font: QFont) -> None:
        """将字体应用到编辑器

        Args:
            font: 要应用的 QFont
        """
        self.setFont(font)

    def is_valid(self, value) -> bool:
        """校验值是否为整数且在范围内

        Args:
            value: 待校验的值

        Returns:
            True 为合法整数且在 [_min, _max] 内
        """
        if value is None:
            return False
        try:
            v = int(value)
            return self._min <= v <= self._max
        except ValueError, TypeError:
            return False

    def format_display(self, value) -> str:
        """将值格式化为显示文本

        当 show_sign=True 时，正值显示 "+N" 格式。

        Args:
            value: 原始值

        Returns:
            显示文本
        """
        if value is None:
            return ""
        try:
            v = int(value)
            if self._show_sign and v >= 0:
                return f"+{v}"
            return str(v)
        except ValueError, TypeError:
            return str(value)

    # ========== 内部槽 ==========

    def _on_value_changed(self, value: int) -> None:
        """值改变时同步 _value 并发射 dataChanged"""
        self._value = value
        self.dataChanged.emit(self._value)
