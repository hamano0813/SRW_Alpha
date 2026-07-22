"""
映射下拉框 - 数值与文本映射单选

通过 mapping 字典实现 数值 ↔ 显示文本 的映射。
下拉选项显示文本，选中后存储对应的数值。
内嵌 qfluentwidgets ComboBox，纯信号槽收发。

Classes:
    MappingCombo: 映射下拉框
"""

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QWidget
from qfluentwidgets import ComboBox, MenuAnimationType, setFont


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

        if self._VIEW_QSS:
            existing = menu.view.styleSheet()
            menu.view.setStyleSheet(existing + "\n" + self._VIEW_QSS)

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


class MappingCombo(QWidget):
    """映射下拉框 - 显示文本，存储数值

    通过 mapping 字典配置选项，选中后发射 valueChanged(int)。
    """

    valueChanged = Signal(int)

    def __init__(self, mapping: dict[int, str] | None = None, parent=None):
        """初始化映射下拉框

        Args:
            mapping: {数值: 显示文本} 字典
            parent:  父 QWidget
        """
        super().__init__(parent)
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

    # ========== 数据接口 ==========

    def set_value(self, value: int) -> None:
        """设置当前选中项"""
        self._combo.blockSignals(True)
        idx = self._combo.findData(value)
        if idx >= 0:
            self._combo.setCurrentIndex(idx)
        self._combo.blockSignals(False)

    def value(self) -> int:
        """获取当前选中项数值"""
        idx = self._combo.currentIndex()
        if idx >= 0:
            return self._combo.itemData(idx)
        return -1

    # ========== 下拉菜单字体 ==========

    def set_dropdown_font(self, font: QFont) -> None:
        """设置下拉菜单项的字体（QSS + !important 覆盖 delegate）"""
        self._combo.set_view_font_qss(font.family(), font.pixelSize())

    # ========== 映射接口 ==========

    def set_mapping(self, mapping: dict[int, str]) -> None:
        """更新选项列表，保持当前选中值（全程阻塞信号）

        Args:
            mapping: {数值: 显示文本} 字典
        """
        current_value = self.value()
        self._mapping = mapping
        self._combo.blockSignals(True)
        self._populate_items()
        if current_value >= 0:
            idx = self._combo.findData(current_value)
            if idx >= 0:
                self._combo.setCurrentIndex(idx)
        self._combo.blockSignals(False)

    def _populate_items(self) -> None:
        """按 mapping 填充下拉选项"""
        self._combo.clear()
        for value, text in self._mapping.items():
            self._combo.addItem(text, userData=value)

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
        self._combo.setFont(font)

    def resetUI(self) -> None:
        """从全局配置刷新字体"""
        setFont(self._combo)

    # ========== 内部槽 ==========

    def _on_index_changed(self, index: int) -> None:
        """选中项变化时发射 valueChanged"""
        if index < 0:
            return
        self.valueChanged.emit(self._combo.itemData(index))
