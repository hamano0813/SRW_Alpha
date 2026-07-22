"""
BitCheckList Bit 位多选列表 - 用复选框列表编辑二进制 bit 位数据

每个选项对应一个 bit 位，使用 qfluentwidgets ListWidget 承载，
内部用 CheckBox 控件，外观与程序中其他地方一致。
适合用于能力强列表、移动类型等需要全部可见的场景。

放置于 widgets/panel/ 子包，供面板编辑器使用。

Classes:
    BitCheckList: Bit 位多选列表
"""

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QListWidgetItem, QWidget
from qfluentwidgets import CheckBox, ListWidget, setFont

from .panel_editor import PanelEditor


class _CheckBoxItemWidget(QWidget):
    """ListWidget 项目的复选框包装控件

    为每个 bit 位提供一个带文字的 CheckBox，点击切换时发出 toggled 信号。
    """

    toggled = Signal(bool)

    def __init__(self, text: str, checked: bool = False, parent=None):
        """初始化复选框项目

        Args:
            text:    选项标签文本
            checked: 初始选中状态
            parent:  父 QWidget
        """
        super().__init__(parent)

        self._check = CheckBox(text, self)
        self._check.setChecked(checked)
        self._check.toggled.connect(self.toggled.emit)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        layout.addWidget(self._check)
        self.setFixedHeight(32)

    def setText(self, text: str) -> None:
        """更新 CheckBox 文字（translateUI 时调用）"""
        self._check.setText(text)


class BitCheckList(PanelEditor):
    """Bit 位多选列表 - 用 ListWidget + CheckBox 编辑二进制 bit 位数据

    显示一个带 qfluentwidgets 风格的列表，每个选项对应一个 bit 位。
    修改后自动写回数据字典。
    支持滚动（适用于 31 项等长列表）。
    """

    def __init__(
        self, field: str, values: list[str] | None = None, parent=None
    ):
        """初始化 Bit 位多选列表

        Args:
            field:  数据字典中对应的键名
            values: 每个 bit 位的显示文本列表，下标即 bit 位
            parent: 父 QWidget
        """
        super().__init__(field, parent)
        self._values: list[str] = values or []
        self._items: list[QListWidgetItem] = []

        # ========== ListWidget（qfluentwidgets 风格） ==========

        self._list = ListWidget(self)
        self._list.setSelectionMode(
            ListWidget.SelectionMode.NoSelection
        )
        self._list.setViewportMargins(0, 0, 0, 0)

        # ========== 整体布局 ==========

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._list)

        # ========== 初始构建 ==========

        for i, v in enumerate(self._values):
            self._add_item(i, v)

    # ========== 项目管理 ==========

    def _add_item(self, idx: int, text: str) -> _CheckBoxItemWidget:
        """添加一个列表项

        Args:
            idx:  bit 位索引
            text: 显示文本

        Returns:
            创建的复选框包装控件
        """
        is_set = (
            bool(self._value & (1 << idx))
            if self._value is not None
            else False
        )

        widget = _CheckBoxItemWidget(text, is_set)
        widget.toggled.connect(
            lambda checked, i=idx: self._on_toggled(i, checked)
        )

        item = QListWidgetItem()
        item.setSizeHint(QSize(0, 32))
        self._list.addItem(item)
        self._list.setItemWidget(item, widget)
        self._items.append(item)
        return widget

    # ========== 选项配置 ==========

    def set_values(self, values: list[str]) -> None:
        """设置 bit 位显示文本列表，同步更新 ListWidget

        更新已有项目文字、移除多余项目、新增不足项目。

        Args:
            values: 每个 bit 位的显示文本，下标即 bit 位
        """
        self._values = values

        old_n = len(self._items)
        new_n = len(values)

        # 更新已有项目的 CheckBox 文字
        for i in range(min(old_n, new_n)):
            widget = self._list.itemWidget(self._items[i])
            if isinstance(widget, _CheckBoxItemWidget):
                widget.setText(values[i])

        # 移除多余项目
        for item in self._items[new_n:]:
            self._list.takeItem(self._list.row(item))
        if old_n > new_n:
            del self._items[new_n:]

        # 新增项目
        for i in range(old_n, new_n):
            self._add_item(i, values[i])

        self.format_value()

    def get_values(self) -> list[str]:
        """返回当前 bit 位显示文本列表

        Returns:
            显示文本列表
        """
        return self._values

    # ========== 位操作 ==========

    def format_value(self) -> None:
        """刷新各列表项 CheckBox 的选中状态（基类扩展点）"""
        if self._value is None:
            for item in self._items:
                widget = self._list.itemWidget(item)
                if isinstance(widget, _CheckBoxItemWidget):
                    widget._check.setChecked(False)
            return

        for i, item in enumerate(self._items):
            cb_widget = self._list.itemWidget(item)
            if isinstance(cb_widget, _CheckBoxItemWidget):
                cb_widget._check.setChecked(
                    bool(self._value & (1 << i))
                )

    def _on_toggled(self, idx: int, checked: bool) -> None:
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

        self._emit_data_changed()

    # ========== 字体 ==========

    def apply_font(self, font: QFont) -> None:
        """设置编辑器字体，应用到所有 CheckBox

        Args:
            font: 要应用的 QFont
        """
        for item in self._items:
            widget = self._list.itemWidget(item)
            if isinstance(widget, _CheckBoxItemWidget):
                widget._check.setFont(font)

    def resetUI(self):
        """从全局配置刷新字体"""
        setFont(self)
        setFont(self._list)
        for item in self._items:
            widget = self._list.itemWidget(item)
            if isinstance(widget, _CheckBoxItemWidget):
                setFont(widget)
                widget._check.setFont(widget.font())
        super().resetUI()
