"""
BitComboBox 多选下拉框 - 用下拉复选框编辑二进制 bit 位数据

每个选项对应一个 bit 位，下拉菜单中嵌入 qfluentwidgets 的 CheckBox 控件，
与程序中其他地方使用的 CheckBox 外观完全一致。
点击切换时菜单保持打开（不自动关闭），支持多选。
修改后自动写回数据字典。

放置于 widgets/panel/ 子包，供面板编辑器使用。

Classes:
    BitComboBox: Bit 位多选下拉框
"""

from PySide6.QtCore import QPoint, QSize, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from qfluentwidgets import CheckBox, ComboBox, MenuAnimationType, RoundMenu, setFont

from .panel_editor import PanelEditor


class _CheckBoxItemWidget(QWidget):
    """包装 qfluentwidgets CheckBox 的菜单项控件

    为每个 bit 位提供一个带文字的 CheckBox，点击切换时发出 toggled 信号。
    通过重写 sizeHint 限定宽度，避免菜单被 CheckBox 文字撑宽。

    默认 RoundMenu 布局边距为 (12, 8, 12, 20)，视图需额外 +2 px（见
    MenuActionListWidget.adjustSize 内部 QSize 填充）。
    """

    toggled = Signal(bool)

    def __init__(self, text: str, checked: bool = False, width: int = 120, parent=None):
        """初始化复选框菜单项

        Args:
            text:    选项标签文本
            checked: 初始选中状态
            width:   控件的目标宽度（px），用于防止菜单过宽
            parent:  父 QWidget
        """
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


class _ComboButton(ComboBox):
    """继承 qfluentwidgets ComboBox 完整样式，替换点击行为"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setText("")

    def mouseReleaseEvent(self, e):
        """跳过 ComboBox._toggleComboMenu，由 BitComboBox._show_menu 接管"""
        super(ComboBox, self).mouseReleaseEvent(e)


class _StayOpenMenu(RoundMenu):
    """可多选的菜单 - 点击项目时不关闭菜单"""

    def exec(self, pos, ani=True, aniType=MenuAnimationType.DROP_DOWN):
        """绕过 PySide6 C++ 重载解析，直接调用 Python 层的 RoundMenu.exec"""
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


class BitComboBox(PanelEditor):
    """Bit 位多选下拉框 - 用下拉复选框编辑二进制 bit 位数据

    显示一个下拉按钮，点击弹出带 CheckBox 控件的菜单。
    每个选项对应一个 bit 位，选中项用 sep 拼接后显示在按钮上。
    空值时按钮显示为 "--"。

    Signals:
        dataChanged: 编辑确认后发射，携带当前数据字典
    """

    def __init__(self, field: str, values: list[str] | None = None, sep: str = "", parent=None):
        """初始化 Bit 位多选下拉框

        Args:
            field:  数据字典中对应的键名
            values: 每个 bit 位的显示文本列表，下标即 bit 位
            sep:    选中项拼接时的分隔符，默认空字符串
            parent: 父 QWidget
        """
        super().__init__(field, parent)
        self._values: list[str] = values or []
        self._sep: str = sep
        self._menu: _StayOpenMenu | None = None

        # ========== 显示按钮（qfluentwidgets 风格） ==========

        self._button = _ComboButton(self)
        self._button.setObjectName("bitComboBoxButton")
        self._button.setFixedHeight(30)
        self._button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._button.clicked.connect(self._show_menu)

        # ========== 布局 ==========

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._button)

    # ========== 选项配置 ==========

    def set_values(self, values: list[str]) -> None:
        """设置 bit 位显示文本列表，同时更新已打开的菜单

        Args:
            values: 每个 bit 位的显示文本，下标即 bit 位
        """
        self._values = values

        # 若菜单已打开，实时更新其中的 CheckBox 文字（translateUI 时触发）
        if self._menu:
            for i in range(self._menu.view.count()):
                item = self._menu.view.item(i)
                widget = self._menu.view.itemWidget(item)
                if isinstance(widget, _CheckBoxItemWidget) and i < len(values):
                    widget.setText(values[i])

        self.format_value()

    def get_values(self) -> list[str]:
        """返回当前 bit 位显示文本列表

        Returns:
            显示文本列表
        """
        return self._values

    def set_separator(self, sep: str) -> None:
        """设置选中项拼接分隔符

        Args:
            sep: 拼接分隔符
        """
        self._sep = sep
        self.format_value()

    # ========== 菜单 ==========

    def _show_menu(self) -> None:
        """点击按钮时弹出多选菜单"""
        if not self._values:
            return

        menu = _StayOpenMenu(self.tr(""), self)
        menu.setObjectName("bitComboBoxMenu")

        # 左边距置 0 让内容靠左，右边距 24 保持窗口总宽不变
        menu.hBoxLayout.setContentsMargins(0, 8, 0, 20)
        item_w = self._button.width() - 2

        for i, v in enumerate(self._values):
            is_set = bool(self._value & (1 << i)) if self._value is not None else False
            widget = _CheckBoxItemWidget(v, is_set, width=item_w)
            widget.setFixedWidth(item_w)  # addWidget 内部用 widget.size() 作初始 hint
            widget.toggled.connect(lambda checked, idx=i: self._on_bit_toggled(idx, checked))
            menu.addWidget(widget, selectable=False)

        menu.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        menu.closedSignal.connect(lambda: self._on_menu_closed(menu))

        self._menu = menu
        # 在按钮正下方弹出
        pos = self._button.mapToGlobal(QPoint(0, self._button.height()))
        menu.exec(pos, True, MenuAnimationType.DROP_DOWN)

    def _on_menu_closed(self, menu: _StayOpenMenu) -> None:
        """菜单关闭时的清理

        Args:
            menu: 刚关闭的菜单实例
        """
        if self._menu is menu:
            self._menu = None

    def _on_bit_toggled(self, idx: int, checked: bool) -> None:
        """某个 bit 位选中状态变化

        Args:
            idx:    bit 位索引
            checked: 是否选中
        """
        if self._value is None:
            self._value = 0

        if checked:
            self._value |= 1 << idx
        else:
            self._value &= ~(1 << idx)

        self._update_button_text()
        self._emit_data_changed()

    # ========== 显示刷新 ==========

    def format_value(self) -> None:
        """刷新按钮显示（基类扩展点）"""
        self._update_button_text()

    def _update_button_text(self) -> None:
        """根据当前值刷新按钮文本"""
        if self._value is None:
            self._button.setText("--")
            return

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

        self._button.setText(text)

    # ========== 字体 ==========

    def apply_font(self, font: QFont) -> None:
        """设置编辑器字体，应用到内部按钮

        Args:
            font: 要应用的 QFont
        """
        self._button.setFont(font)

    def resetUI(self):
        """从全局配置刷新主框字体"""
        setFont(self._button)
