"""
映射微调框 — 继承 QSpinBox + TableEditor，透明背景，左减右加按钮布局

通过 mapping 字典实现 数字 ↔ 显示文本 的转换。
步进时仅在 mapping 的有效 key 范围内循环。
无焦点横线、无文本选中、仅按钮步进。

Classes:
    MappingSpinBox: 映射微调框
"""

from typing import Any

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath
from PySide6.QtWidgets import QSpinBox, QToolButton
from qfluentwidgets import isDarkTheme

from .tableeditor import TableEditor


class _ArrowButton(QToolButton):
    """单方向箭头按钮 — 左箭头（步进-）或右箭头（步进+）"""

    def __init__(self, right: bool, parent=None):
        super().__init__(parent)
        self._right = right
        self.setFixedSize(24, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, e):
        """根据按钮方向调用 stepUp 或 stepDown

        Args:
            e: 鼠标事件
        """
        if self._right:
            self.parent().stepUp()
        else:
            self.parent().stepDown()

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


class MappingSpinBox(QSpinBox, TableEditor):
    """映射微调框 — 透明背景，左右按钮，数值居中

    左侧步进-（左三角）、中间数值（居中）、右侧步进+（右三角）。
    禁止键盘手动输入，仅由按钮步进。
    步进仅在 mapping 的有效 key 范围内循环。
    """

    def __init__(self, mapping: dict[int, str] | None = None, parent=None):
        """初始化映射微调框

        Args:
            mapping: {数值: 显示文本} 字典，按 key 排序后确定步进顺序
            parent: 父 QWidget
        """
        self._mapping: dict[int, str] = mapping or {}
        self._sorted_keys: list[int] = sorted(self._mapping.keys())

        QSpinBox.__init__(self, parent)
        TableEditor.__init__(self, parent)

        # ========== 基础样式 ==========

        self.setFrame(False)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.setFixedHeight(28)

        if self._sorted_keys:
            self.setRange(self._sorted_keys[0], self._sorted_keys[-1])

        # ========== 行编辑：透明 + 居中 + 只读 ==========

        le = self.lineEdit()
        le.setReadOnly(True)
        le.setFrame(False)
        le.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        le.setAlignment(Qt.AlignmentFlag.AlignCenter)
        le.setStyleSheet("background: transparent; border: none;")
        le.selectionChanged.connect(lambda: le.setSelection(0, 0))

        # ========== 左右按钮（手动定位） ==========

        self._btn_left = _ArrowButton(False, self)
        self._btn_right = _ArrowButton(True, self)

        # ========== 信号 ==========

        self.valueChanged.connect(self._on_value_changed)

    def resizeEvent(self, e):
        """手动定位左右按钮

        Args:
            e: 调整大小事件
        """
        super().resizeEvent(e)
        bw = self._btn_left.width()
        y = (self.height() - self._btn_left.height()) // 2
        self._btn_left.move(2, y)
        self._btn_right.move(self.width() - bw - 2, y)

    # ========== 映射接口 ==========

    def set_mapping(self, mapping: dict[int, str]) -> None:
        """更新映射表并调整范围

        Args:
            mapping: {数值: 显示文本} 字典
        """
        self._mapping = mapping
        self._sorted_keys = sorted(self._mapping.keys())
        if self._sorted_keys:
            self.setRange(self._sorted_keys[0], self._sorted_keys[-1])

    def mapping(self) -> dict[int, str]:
        """获取当前映射表

        Returns:
            {数值: 显示文本} 字典
        """
        return self._mapping

    # ========== 值 ↔ 文本转换 ==========

    def textFromValue(self, value: int) -> str:
        """数值 → 显示文本

        Args:
            value: 数值

        Returns:
            对应的显示文本
        """
        return self._mapping.get(value, str(value))

    def valueFromText(self, text: str) -> int:
        """显示文本 → 数值

        Args:
            text: 显示文本

        Returns:
            对应的数值
        """
        for k, v in self._mapping.items():
            if v == text:
                return k
        return self.value()

    def stepBy(self, steps: int) -> None:
        """沿 mapping 的 key 顺序步进，不超出边界

        Args:
            steps: 步数（正向/负向）
        """
        if not self._sorted_keys:
            super().stepBy(steps)
            return
        current = self.value()
        try:
            idx = self._sorted_keys.index(current)
        except ValueError:
            idx = 0
        new_idx = max(0, min(len(self._sorted_keys) - 1, idx + steps))
        self.setValue(self._sorted_keys[new_idx])

    def stepEnabled(self):
        """允许步进方向 — 在边界处禁用对应方向

        Returns:
            StepEnabledFlag 组合
        """
        if not self._sorted_keys:
            return super().stepEnabled()
        current = self.value()
        try:
            idx = self._sorted_keys.index(current)
        except ValueError:
            return QSpinBox.StepEnabledFlag.StepUpEnabled | QSpinBox.StepEnabledFlag.StepDownEnabled
        flags = QSpinBox.StepEnabledFlag(QSpinBox.StepEnabledFlag.StepNone)
        if idx > 0:
            flags |= QSpinBox.StepEnabledFlag.StepDownEnabled
        if idx < len(self._sorted_keys) - 1:
            flags |= QSpinBox.StepEnabledFlag.StepUpEnabled
        return flags

    # ========== TableEditor 数据协议 ==========

    def set_value(self, value) -> None:
        """存入数值并刷新显示

        Args:
            value: 整数数值
        """
        TableEditor.set_value(self, value)

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
        """校验值是否为整数或可转为整数

        Args:
            value: 待校验的值

        Returns:
            True 为可转为整数
        """
        try:
            int(value)
            return True
        except (TypeError, ValueError):
            return False

    def format_display(self, value) -> str:
        """将数值格式化为显示文本

        Args:
            value: 原始值

        Returns:
            映射后的显示文本
        """
        if value is None:
            return ""
        try:
            return self.textFromValue(int(value))
        except Exception:
            return str(value)

    def parse_display(self, text: str) -> Any:
        """将显示文本解析为数值

        Args:
            text: 显示文本

        Returns:
            对应的数值
        """
        return self.valueFromText(text)

    # ========== 内部槽 ==========

    def _on_value_changed(self, value: int) -> None:
        """值改变时同步 _value 并发射 dataChanged"""
        self._value = value
        self.dataChanged.emit(self._value)
