"""
映射微调框 - 数值与文本映射单选

直接继承 VerticalSpinBox，无 QWidget 壳。
通过 mapping 字典实现 数值 ↔ 显示文本 的转换，
步进时仅在 mapping 的有效 key 范围内循环。

Classes:
    CommonMappingSpin: 映射微调框
"""

from PySide6.QtCore import QEvent, Qt
from PySide6.QtGui import QFont

from gui.widget.abstract import VerticalSpinBox


class CommonMappingSpin(VerticalSpinBox):
    """映射微调框 - 数值与文本映射单选

    直接继承 VerticalSpinBox，使用 editable=True（与 CommonNumberSpin 一致），
    通过 eventFilter 拦截键盘输入替代 read-only，避免触发 SpinBox:read-only QSS。
    """

    def __init__(self, mapping: dict[int, str] | None = None, parent=None):
        """初始化映射微调框

        Args:
            mapping: {数值: 显示文本} 字典
            parent:  父 QWidget
        """
        super().__init__(parent, editable=True)

        # 禁止用户直接输入（仅按钮步进）
        le = self.lineEdit()
        le.setReadOnly(True)
        le.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        le.setCursor(Qt.CursorShape.ArrowCursor)
        le.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        le.installEventFilter(self)

        self._map_mapping: dict[int, str] = mapping or {}
        self._sorted_keys: list[int] = sorted(self._map_mapping.keys())
        self._current_value: int = 0

        if self._sorted_keys:
            self.setRange(self._sorted_keys[0], self._sorted_keys[-1])

        self.valueChanged.connect(self._on_value_changed)

    # ========== 键盘拦截 ==========

    def eventFilter(self, obj, e):
        """阻止键盘直接编辑，仅允许按钮步进"""
        if obj == self.lineEdit():
            t = e.type()
            if t in (QEvent.Type.KeyPress, QEvent.Type.KeyRelease,
                     QEvent.Type.InputMethod, QEvent.Type.ShortcutOverride):
                return True
        return super().eventFilter(obj, e)

    # ========== 数据接口 ==========

    def set_value(self, value: int) -> None:
        """设置当前值并刷新显示"""
        self._current_value = value
        self.blockSignals(True)
        self.setValue(int(value))
        self.blockSignals(False)

    def value(self) -> int:
        """获取当前值"""
        return self._current_value

    # ========== 映射接口 ==========

    def set_mapping(self, mapping: dict[int, str]) -> None:
        """更新映射表并调整范围（保持当前选中值）

        Args:
            mapping: {数值: 显示文本} 字典
        """
        old_value = self._current_value
        self._map_mapping = mapping
        self._sorted_keys = sorted(self._map_mapping.keys())
        if self._sorted_keys:
            self.setRange(self._sorted_keys[0], self._sorted_keys[-1])
        if old_value in self._sorted_keys:
            self.blockSignals(True)
            self.setValue(old_value)
            self.blockSignals(False)

    # ========== 显示格式 ==========

    def textFromValue(self, value: int) -> str:
        """数值 → 显示文本"""
        return self._map_mapping.get(value, str(value))

    def valueFromText(self, text: str) -> int:
        """显示文本 → 数值"""
        for k, v in self._map_mapping.items():
            if v == text:
                return k
        return self.value()

    def stepBy(self, steps: int) -> None:
        """按映射键列表步进"""
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

    # ========== 字体 ==========

    def apply_font(self, font: QFont | dict) -> None:
        """设置编辑器字体"""
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
        self.setFont(font)

    def resetUI(self) -> None:
        """从全局配置刷新字体"""
        super().resetUI()

    # ========== 内部 ==========

    def _on_value_changed(self, value: int) -> None:
        """值改变时更新内部状态"""
        self._current_value = value
