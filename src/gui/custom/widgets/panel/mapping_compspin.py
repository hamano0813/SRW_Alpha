"""
MappingCompSpin 映射微调框 - 数值与文本映射单选

通过 mapping 字典实现 数值 ↔ 显示文本 的转换。
步进时仅在 mapping 的有效 key 范围内循环。
内嵌自定义垂直微调框，使用 FluentIcon 箭头直接步进，无 flyout。

放置于 widgets/panel/ 子包，供面板编辑器使用。

Classes:
    MappingCompSpin: 映射微调框
"""

from typing import Any

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QFont, QPainter
from PySide6.QtWidgets import QSpinBox, QToolButton, QVBoxLayout, QWidget
from qfluentwidgets.common.icon import FluentIcon as FIF
from qfluentwidgets.common.style_sheet import isDarkTheme
from qfluentwidgets.components.widgets.spin_box import SpinBoxBase

from .panel_editor import PanelEditor


# ========== 自定义箭头按钮 ==========


class _SpinArrowButton(QToolButton):
    """单个方向箭头按钮 - 使用 FluentIcon ARROW_DOWN

    上箭头通过旋转 180° 实现，颜色规则与 ComboBox 一致。
    """

    def __init__(self, up: bool, parent=None):
        super().__init__(parent=parent)
        self._up = up
        self._hovered = False
        self.setFixedSize(26, 16)
        self.setCursor(Qt.PointingHandCursor)

    def enterEvent(self, e):
        self._hovered = True
        self.update()
        super().enterEvent(e)

    def leaveEvent(self, e):
        self._hovered = False
        self.update()
        super().leaveEvent(e)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)

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
        kwargs = {} if isDarkTheme() else {"fill": "#646464"}

        if self._up:
            painter.save()
            painter.translate(x + s / 2, y + s / 2)
            painter.rotate(180)
            FIF.ARROW_DOWN.render(painter, QRectF(-s / 2, -s / 2, s, s), **kwargs)
            painter.restore()
        else:
            FIF.ARROW_DOWN.render(painter, QRectF(x, y, s, s), **kwargs)


# ========== 垂直微调框 ==========


class _VerticalSpinBox(SpinBoxBase, QSpinBox):
    """垂直微调框 - 右置上下箭头按钮直接步进，无 flyout"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lineEdit().setTextMargins(0, 0, 26, 0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)

        # 右侧垂直按钮面板
        panel = QWidget(self)
        panel.setFixedWidth(26)
        vbox = QVBoxLayout(panel)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)

        self._up_btn = _SpinArrowButton(up=True)
        self._dn_btn = _SpinArrowButton(up=False)
        vbox.addWidget(self._up_btn)
        vbox.addWidget(self._dn_btn)

        self.hBoxLayout.addWidget(panel, 0, Qt.AlignRight)
        self.hBoxLayout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self._up_btn.clicked.connect(self.stepUp)
        self._dn_btn.clicked.connect(self.stepDown)

    def setSymbolVisible(self, isVisible: bool):
        super().setSymbolVisible(isVisible)
        self._up_btn.setVisible(isVisible)
        self._dn_btn.setVisible(isVisible)


# ========== MappingCompSpin ==========


class MappingCompSpin(PanelEditor):
    """映射微调框 - 数值与文本映射单选

    步进仅在 mapping 的有效 key 范围内循环。
    显示文本为 mapping 中对应的值。
    """

    def __init__(self, field: str, mapping: dict[int, str] | None = None, parent=None):
        super().__init__(field, parent)

        self._map_mapping: dict[int, str] = mapping or {}
        self._sorted_keys: list[int] = sorted(self._map_mapping.keys())

        # ========== 内嵌微调框 ==========

        self._spin = _ProxySpin(self._map_mapping, self._sorted_keys, self)
        if self._sorted_keys:
            self._spin.setRange(self._sorted_keys[0], self._sorted_keys[-1])
        self._spin.valueChanged.connect(self._on_value_changed)

        # ========== 布局 ==========

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._spin)

    # ========== 映射接口 ==========

    def set_mapping(self, mapping: dict[int, str]) -> None:
        self._map_mapping = mapping
        self._sorted_keys = sorted(self._map_mapping.keys())
        if self._sorted_keys:
            self._spin.setRange(self._sorted_keys[0], self._sorted_keys[-1])
        self._spin.set_mapping(mapping, self._sorted_keys)

    # ========== PanelEditor 数据协议 ==========

    def set_row(self, row: int) -> None:
        super().set_row(row)
        self._spin.blockSignals(True)
        if self._value is not None:
            self._spin.setValue(int(self._value))
        self._spin.blockSignals(False)

    def format_value(self) -> None:
        self._spin.blockSignals(True)
        if self._value is not None:
            self._spin.setValue(int(self._value))
        self._spin.blockSignals(False)

    def apply_font(self, font: QFont | dict) -> None:
        if isinstance(font, dict):
            qfont = QFont()
            family = font.get("family")
            size = font.get("size")
            weight = font.get("weight")
            italic = font.get("italic")
            if family:
                qfont.setFamily(family)
            if size:
                qfont.setPixelSize(size)
            if weight:
                qfont.setWeight(weight)
            if italic:
                qfont.setItalic(italic)
            font = qfont
        self._spin.setFont(font)

    # ========== 内部槽 ==========

    def _on_value_changed(self, value: int) -> None:
        self._value = value
        self._emit_data_changed()


# ========== 代理微调框 ==========


class _ProxySpin(_VerticalSpinBox):
    """映射步进微调框 - 代理 _VerticalSpinBox 的 textFromValue / stepBy"""

    def __init__(self, mapping: dict[int, str], sorted_keys: list[int], parent=None):
        super().__init__(parent)
        self._map_mapping = mapping
        self._sorted_keys = sorted_keys

    def set_mapping(self, mapping: dict[int, str], sorted_keys: list[int]):
        self._map_mapping = mapping
        self._sorted_keys = sorted_keys

    def textFromValue(self, value: int) -> str:
        return self._map_mapping.get(value, str(value))

    def valueFromText(self, text: str) -> int:
        for k, v in self._map_mapping.items():
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
