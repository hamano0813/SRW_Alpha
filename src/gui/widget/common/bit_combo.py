"""
Bit 位多选下拉框 - 用下拉复选框编辑二进制 bit 位数据

每个选项对应一个 bit 位，下拉菜单中嵌入 qfluentwidgets 的 CheckBox 控件。
点击切换时菜单保持打开（不自动关闭），支持多选。
纯信号槽收发，不感知 model。

Classes:
    CommonBitCombo: Bit 位多选下拉框
"""

from PySide6.QtCore import QPoint, QSize, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QWidget
from qfluentwidgets import CheckBox, ComboBox, MenuAnimationType, RoundMenu, setFont


class _CheckBoxItemWidget(QWidget):
    """包装 qfluentwidgets CheckBox 的菜单项控件"""

    toggled = Signal(bool)

    def __init__(self, text: str, checked: bool = False, width: int = 120, parent=None):
        super().__init__(parent)
        self._target_width = width

        self._check = CheckBox(text, self)
        self._check.setChecked(checked)
        self._check.toggled.connect(self.toggled.emit)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 16)
        layout.addWidget(self._check)
        self.setFixedHeight(30)

    def sizeHint(self) -> QSize:
        """返回限定宽度，阻止 QListWidgetItem 读取 CheckBox 的自然宽度"""
        return QSize(self._target_width, 30)

    def setText(self, text: str) -> None:
        """更新 CheckBox 文字（translateUI 时调用）"""
        self._check.setText(text)


class _StayOpenMenu(RoundMenu):
    """可多选的菜单 - 点击项目时不关闭菜单"""

    def exec(self, pos, ani=True, aniType=MenuAnimationType.DROP_DOWN):
        self.view.adjustSize(pos, aniType)
        self.adjustSize()
        return RoundMenu.exec(self, pos, ani, aniType)

    def _onItemClicked(self, item):
        action = item.data(Qt.ItemDataRole.UserRole)
        if action not in self._actions or not action.isEnabled():
            return
        if self.view.itemWidget(item) and not action.property("selectable"):
            return
        action.trigger()


class CommonBitCombo(ComboBox):
    """Bit 位多选下拉框 - 用下拉复选框编辑二进制 bit 位数据

    显示一个下拉按钮，点击弹出带 CheckBox 控件的菜单。
    每个选项对应一个 bit 位，选中项用 sep 拼接后显示在按钮上。
    编辑后发射 valueChanged(int) 发射当前 bitmask。
    """

    valueChanged = Signal(int)

    def __init__(self, values: list[str] | None = None, sep: str = "", parent=None):
        """初始化 Bit 位多选下拉框

        Args:
            values: 每个 bit 位的显示文本列表，下标即 bit 位
            sep:    选中项拼接时的分隔符，默认空字符串
            parent: 父 QWidget
        """
        super().__init__(parent)
        self._values: list[str] = values or []
        self._sep: str = sep
        self._value: int = 0
        self._menu: _StayOpenMenu | None = None

        self.setText("")
        self.setObjectName("bitComboBoxButton")
        self.setFixedHeight(33)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self._show_menu)

    # ========== 鼠标事件 ==========

    def mouseReleaseEvent(self, e):
        """跳过 ComboBox._toggleComboMenu，由 _show_menu 接管下拉行为"""
        super(ComboBox, self).mouseReleaseEvent(e)

    # ========== 数据接口 ==========

    def set_value(self, value: int) -> None:
        """设置当前 bitmask 值并刷新显示"""
        self._value = value
        self._update_button_text()

    def value(self) -> int:
        """获取当前 bitmask 值"""
        return self._value

    # ========== 选项配置 ==========

    def set_values(self, values: list[str]) -> None:
        """设置 bit 位显示文本列表，同时更新已打开的菜单"""
        self._values = values
        if self._menu:
            for i in range(self._menu.view.count()):
                item = self._menu.view.item(i)
                widget = self._menu.view.itemWidget(item)
                if isinstance(widget, _CheckBoxItemWidget) and i < len(values):
                    widget.setText(values[i])
        self._update_button_text()

    def get_values(self) -> list[str]:
        """返回当前 bit 位显示文本列表"""
        return self._values

    def set_separator(self, sep: str) -> None:
        """设置选中项拼接分隔符"""
        self._sep = sep
        self._update_button_text()

    # ========== 菜单 ==========

    def _show_menu(self) -> None:
        """点击按钮时弹出多选菜单"""
        if not self._values:
            return

        menu = _StayOpenMenu(self.tr(""), self)
        menu.setObjectName("bitComboBoxMenu")
        menu.hBoxLayout.setContentsMargins(0, 8, 0, 20)
        item_w = self.width() - 2

        for i, v in enumerate(self._values):
            is_set = bool(self._value & (1 << i))
            widget = _CheckBoxItemWidget(v, is_set, width=item_w)
            widget.setFixedWidth(item_w)
            widget.toggled.connect(lambda checked, idx=i: self._on_bit_toggled(idx, checked))
            menu.addWidget(widget, selectable=False)

        menu.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        menu.closedSignal.connect(lambda: self._on_menu_closed(menu))

        self._menu = menu
        pos = self.mapToGlobal(QPoint(0, self.height()))
        menu.exec(pos, True, MenuAnimationType.DROP_DOWN)

    def _on_menu_closed(self, menu: _StayOpenMenu) -> None:
        if self._menu is menu:
            self._menu = None

    def _on_bit_toggled(self, idx: int, checked: bool) -> None:
        """某个 bit 位选中状态变化"""
        if checked:
            self._value |= 1 << idx
        else:
            self._value &= ~(1 << idx)
        self._update_button_text()
        self.valueChanged.emit(self._value)

    # ========== 显示刷新 ==========

    def _update_button_text(self) -> None:
        """根据当前值刷新按钮文本"""
        parts = []
        for i, v in enumerate(self._values):
            if self._value & (1 << i):
                parts.append(v)

        if parts:
            text = self._sep.join(parts)
        elif self._value != 0:
            text = f"0x{self._value:X}"
        else:
            text = ""

        self.setText(text)

    # ========== 字体 ==========

    def apply_font(self, font: QFont) -> None:
        """设置编辑器字体"""
        self.setFont(font)

    def resetUI(self):
        """从全局配置刷新字体"""
        setFont(self)
