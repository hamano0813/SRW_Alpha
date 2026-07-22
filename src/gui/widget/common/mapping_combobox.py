"""
MappingComboBox 映射下拉框 - 数值与文本映射单选

通过 mapping 字典实现 数值 ↔ 显示文本 的映射。
下拉选项显示文本，选中后存储对应的数值。
内嵌 qfluentwidgets ComboBox，外观与程序其他位置一致。

放置于 widgets/panel/ 子包，供面板编辑器使用。

Classes:
    MappingComboBox: 映射下拉框
"""

from typing import Any

from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy
from qfluentwidgets import ComboBox, MenuAnimationType, setFont

from .panel_editor import PanelEditor


class _MappingCombo(ComboBox):
    """内部 ComboBox — 支持为下拉菜单项设置字体"""

    _VIEW_QSS: str = ""

    def set_view_font_qss(self, family: str, size: int) -> None:
        """保存下拉菜单字体的 QSS"""
        self._VIEW_QSS = (
            "MenuActionListWidget#comboListWidget {"
            f"font-family: '{family}' !important;"
            f"font-size: {size}px !important;"
            "}"
        )

    def _showComboMenu(self):
        """接管菜单显示，在 exec 前对 view 注入字体 QSS"""
        if not self.items:
            return

        menu = self._createComboMenu()
        for item in self.items:
            action = QAction(item.icon, item.text)
            action.setEnabled(item.isEnabled)
            menu.addAction(action)
        menu.view.itemClicked.connect(
            lambda i: self._onItemClicked(self.findText(i.text().lstrip())))

        if menu.view.width() < self.width():
            menu.view.setMinimumWidth(self.width())
            menu.adjustSize()

        menu.setMaxVisibleItems(self.maxVisibleItems())
        menu.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        menu.closedSignal.connect(self._onDropMenuClosed)
        self.dropMenu = menu

        if self.currentIndex() >= 0 and self.items:
            menu.setDefaultAction(menu.actions()[self.currentIndex()])

        # ========== 追加字体 QSS（保留原有样式，仅覆盖字体） ==========

        if self._VIEW_QSS:
            existing = menu.view.styleSheet()
            menu.view.setStyleSheet(existing + "\n" + self._VIEW_QSS)

        # ========== 定位并显示 ==========

        x = -menu.width() // 2 + menu.layout().contentsMargins().left() + self.width() // 2
        pd = self.mapToGlobal(QPoint(x, self.height()))
        hd = menu.view.heightForAnimation(pd, MenuAnimationType.DROP_DOWN)

        pu = self.mapToGlobal(QPoint(x, 0))
        hu = menu.view.heightForAnimation(pu, MenuAnimationType.PULL_UP)

        if hd >= hu:
            menu.view.adjustSize(pd, MenuAnimationType.DROP_DOWN)
            menu.exec(pd, aniType=MenuAnimationType.DROP_DOWN)
        else:
            menu.view.adjustSize(pu, MenuAnimationType.PULL_UP)
            menu.exec(pu, aniType=MenuAnimationType.PULL_UP)


class MappingComboBox(PanelEditor):
    """映射下拉框 - 显示文本，存储数值

    通过 mapping 字典配置选项，选中时自动将数值写回数据字典。
    """

    def __init__(self, field: str, mapping: dict[int, str] | None = None, parent=None):
        """初始化映射下拉框

        Args:
            field:   数据字典中对应的键名
            mapping: {数值: 显示文本} 字典，键按插入顺序排列
            parent:  父 QWidget
        """
        super().__init__(field, parent)
        self._mapping: dict[int, str] = mapping or {}

        # ========== 内嵌下拉框 ==========

        self._combo = _MappingCombo(self)
        self._combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._combo.setMinimumHeight(30)
        self._combo.setMaxVisibleItems(10)
        self._combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self._combo.currentIndexChanged.connect(self._on_index_changed)

        self._populate_items()

        # ========== 布局 ==========

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._combo)

    # ========== 下拉菜单字体 ==========

    def set_dropdown_font(self, font: QFont) -> None:
        """设置下拉菜单项的字体（QSS + !important 覆盖 delegate）

        Args:
            font: QFont 实例（如 fonts.JP_QFONT）
        """
        self._combo.set_view_font_qss(font.family(), font.pixelSize())

    # ========== 映射接口 ==========

    def set_mapping(self, mapping: dict[int, str]) -> None:
        """更新选项列表，保持当前选中值（全程阻塞信号避免触发 dataChanged）

        Args:
            mapping: {数值: 显示文本} 字典
        """
        current_value = self._value
        self._mapping = mapping
        self._combo.blockSignals(True)
        self._populate_items()

        # 尝试恢复选中项
        if current_value is not None:
            idx = self._combo.findData(current_value)
            if idx >= 0:
                self._combo.setCurrentIndex(idx)
        self._combo.blockSignals(False)

    def _populate_items(self) -> None:
        """按 mapping 填充下拉选项"""
        self._combo.clear()
        for value, text in self._mapping.items():
            self._combo.addItem(text, userData=value)

    # ========== PanelEditor 数据协议 ==========

    def set_row(self, row: int) -> None:
        """切换行并刷新控件"""
        super().set_row(row)
        self._sync_combo()

    def format_value(self) -> None:
        """刷新显示"""
        self._sync_combo()

    def _sync_combo(self) -> None:
        """将当前 _value 同步到下拉框选中项"""
        self._combo.blockSignals(True)
        if self._value is not None:
            idx = self._combo.findData(self._value)
            if idx >= 0:
                self._combo.setCurrentIndex(idx)
        self._combo.blockSignals(False)

    def apply_font(self, font: QFont | dict) -> None:
        """设置编辑器字体

        Args:
            font: QFont 实例或字体属性字典
        """
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
        self._combo.setFont(font)

    def resetUI(self) -> None:
        """从全局配置刷新字体"""
        setFont(self._combo)

    # ========== 内部槽 ==========

    def _on_index_changed(self, index: int) -> None:
        """选中项变化时同步 _value 并写回字典"""
        if index < 0:
            return
        self._value = self._combo.itemData(index)
        self._emit_data_changed()
