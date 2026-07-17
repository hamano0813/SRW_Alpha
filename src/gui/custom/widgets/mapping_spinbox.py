"""
映射微调框 — 透明背景 QSpinBox，左减右加按钮布局

通过 mapping 字典实现 数字 ↔ 显示文本 的转换。
步进时仅在 mapping 的有效 key 范围内循环。
无焦点横线、无文本选中、仅按钮步进。

Classes:
    MappingSpinBox: 映射微调框
"""

from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QColor, QPainter, QPainterPath
from PySide6.QtWidgets import QSpinBox, QToolButton
from qfluentwidgets import isDarkTheme


class _ArrowButton(QToolButton):
    """单方向箭头按钮 — 左箭头（步进-）或右箭头（步进+）"""

    def __init__(self, right: bool, parent=None):
        """初始化箭头按钮

        Args:
            right: True 为右箭头（步进+），False 为左箭头（步进-）
            parent: 父 QWidget
        """
        super().__init__(parent)
        self._right = right
        self.setFixedSize(24, 26)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, e):
        if self._right:
            self.parent().stepUp()
        else:
            self.parent().stepDown()

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)

        color = QColor(200, 200, 200) if isDarkTheme() else QColor(80, 80, 80)
        painter.setBrush(color)

        s = 5
        cx = self.width() / 2
        cy = self.height() / 2

        if self._right:
            # 右三角：顶点朝右
            path = QPainterPath()
            path.moveTo(QPointF(cx + s, cy))
            path.lineTo(QPointF(cx - s, cy - s))
            path.lineTo(QPointF(cx - s, cy + s))
        else:
            # 左三角：顶点朝左
            path = QPainterPath()
            path.moveTo(QPointF(cx - s, cy))
            path.lineTo(QPointF(cx + s, cy - s))
            path.lineTo(QPointF(cx + s, cy + s))

        path.closeSubpath()
        painter.drawPath(path)


class MappingSpinBox(QSpinBox):
    """映射微调框 — 透明背景，左右按钮，数值居中

    左侧步进-（向下箭头）、中间数值（居中）、右侧步进+（向上箭头）。
    禁止键盘手动输入，仅由按钮步进。
    步进仅在 mapping 的有效 key 范围内循环。

    使用示例：
        spin = MappingSpinBox({0: "None", 1: "A", 2: "B"})
        spin.setValue(1)  # 显示 "A"，值为 1
    """

    def __init__(self, mapping: dict[int, str] | None = None, parent=None):
        """初始化映射微调框

        Args:
            mapping: {数值: 显示文本} 字典，按 key 排序后确定步进顺序
            parent: 父 QWidget
        """
        self._mapping: dict[int, str] = mapping or {}
        self._sorted_keys: list[int] = sorted(self._mapping.keys())

        super().__init__(parent)

        # ========== 基础样式 ==========

        self.setFrame(False)
        self.setAttribute(Qt.WidgetAttribute.WA_MacShowFocusRect, False)
        self.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.setFixedHeight(28)

        if self._sorted_keys:
            self.setRange(self._sorted_keys[0], self._sorted_keys[-1])

        # ========== 行编辑：透明 + 居中 + 只读 ==========

        le = self.lineEdit()
        le.setReadOnly(True)
        le.setFrame(False)
        le.setAlignment(Qt.AlignmentFlag.AlignCenter)
        le.setStyleSheet("background: transparent; border: none;")
        le.selectionChanged.connect(le.deselect)

        # ========== 左右按钮（手动定位） ==========

        self._btn_left = _ArrowButton(False, self)   # 左三角 → 步进-
        self._btn_right = _ArrowButton(True, self)   # 右三角 → 步进+

    def resizeEvent(self, e):
        """手动定位左右按钮"""
        super().resizeEvent(e)
        bw = self._btn_left.width()
        y = (self.height() - self._btn_left.height()) // 2
        self._btn_left.move(2, y)
        self._btn_right.move(self.width() - bw - 2, y)

    # ========== 映射接口 ==========

    def set_mapping(self, mapping: dict[int, str]) -> None:
        self._mapping = mapping
        self._sorted_keys = sorted(self._mapping.keys())
        if self._sorted_keys:
            self.setRange(self._sorted_keys[0], self._sorted_keys[-1])

    def mapping(self) -> dict[int, str]:
        return self._mapping

    # ========== 值 ↔ 文本转换 ==========

    def textFromValue(self, value: int) -> str:
        return self._mapping.get(value, str(value))

    def valueFromText(self, text: str) -> int:
        for k, v in self._mapping.items():
            if v == text:
                return k
        return self.value()

    def stepBy(self, steps: int) -> None:
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
