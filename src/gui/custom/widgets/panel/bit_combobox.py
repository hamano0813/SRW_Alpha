"""
BitComboBox 多选下拉框 - 用下拉复选框编辑二进制 bit 位数据

每个选项对应一个 bit 位，下拉菜单中用 CheckIndicator 表示选中状态。
点击切换时菜单保持打开（不自动关闭），支持多选。
修改后自动写回数据字典。

放置于 widgets/panel/ 子包，供面板编辑器使用。

Classes:
    BitComboBox: Bit 位多选下拉框
"""

from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import QVBoxLayout

from qfluentwidgets import CheckableMenu, ComboBox, MenuAnimationType, setFont

from .panel_editor import PanelEditor


class _ComboButton(ComboBox):
    """继承 qfluentwidgets ComboBox 完整样式，替换点击行为"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # ComboBox 默认带 item 管理，此处不需要
        self.setText("")

    def mouseReleaseEvent(self, e):
        """跳过 ComboBox._toggleComboMenu，由 BitComboBox._show_menu 接管"""
        super(ComboBox, self).mouseReleaseEvent(e)
        # QPushButton.mouseReleaseEvent 已 emit clicked，不再调 _toggleComboMenu


class _StayOpenMenu(CheckableMenu):
    """可多选的菜单 - 点击项目时不关闭菜单

    基类 RoundMenu._onItemClicked 默认会关闭菜单。
    本类跳过关闭，仅触发 action 切换选中状态。
    """

    def exec(self, pos, ani=True, aniType=MenuAnimationType.DROP_DOWN):
        """绕过 PySide6 C++ 重载解析，直接调用 Python 层的 RoundMenu.exec"""
        return CheckableMenu.exec(self, pos, ani, aniType)

    def _onItemClicked(self, item):
        action = item.data(Qt.ItemDataRole.UserRole)
        if action not in self._actions or not action.isEnabled():
            return
        if self.view.itemWidget(item) and not action.property("selectable"):
            return
        # 不关闭菜单，只触发 action 切换 checked 状态
        action.trigger()


class BitComboBox(PanelEditor):
    """Bit 位多选下拉框 - 用下拉复选框编辑二进制 bit 位数据

    显示一个下拉按钮，点击弹出带复选框的菜单。
    每个选项对应一个 bit 位，选中项用 sep 拼接后显示在按钮上。
    空值时按钮显示为 "--"。

    Signals:
        dataChanged: 编辑确认后发射，携带当前数据字典
    """

    def __init__(self, field: str, values: list[str] | None = None,
                 sep: str = "", parent=None):
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
        self._button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._button.clicked.connect(self._show_menu)

        # ========== 布局 ==========

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._button)

    # ========== 选项配置 ==========

    def set_values(self, values: list[str]) -> None:
        """设置 bit 位显示文本列表

        Args:
            values: 每个 bit 位的显示文本，下标即 bit 位
        """
        self._values = values
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

        # 在添加 item 前设置最小宽度，确保 adjustSize → setFixedSize 正确锁定宽度
        menu.view.setMinimumWidth(self._button.width())

        for i, v in enumerate(self._values):
            action = QAction(v)
            action.setCheckable(True)
            is_set = bool(self._value & (1 << i)) if self._value is not None else False
            action.setChecked(is_set)
            # 用闭包默认参数绑定当前 i，避免循环中的延时绑定问题
            action.triggered.connect(lambda checked, idx=i: self._on_bit_toggled(idx, checked))
            menu.addAction(action)

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
