"""
精神指令下拉框 - 直接继承 qfluentwidgets ComboBox

通过 {数值: 显示文本} 映射显示精神指令，选中后信号发送对应的数值 ID。

Classes:
    SpiritCombo: 精神指令下拉框
"""

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import QSizePolicy
from qfluentwidgets import ComboBox, MenuAnimationType, getFont, setFont


class SpiritCombo(ComboBox):
    """精神指令下拉框 - 显示文本，存储数值 ID

    直接继承 ComboBox，通过 mapping 字典配置选项。
    选中后通过 valueChanged 发射对应的 key。
    """

    valueChanged = Signal(int)

    _view_qss: str = ""

    def __init__(self, mapping: dict[int, str] | None = None, parent=None):
        """初始化精神指令下拉框

        Args:
            mapping: {数值: 显示文本} 字典
            parent:  父 QWidget
        """
        super().__init__(parent)
        self._mapping: dict[int, str] = mapping or {}

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumWidth(130)
        self.setFixedHeight(33)
        self.setMaxVisibleItems(10)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.currentIndexChanged.connect(self._on_index_changed)

        if mapping:
            self._populate_items()

    # ========== 数据接口 ==========

    def set_mapping(self, mapping: dict[int, str]) -> None:
        """设置选项列表（保持当前选中值）

        Args:
            mapping: {数值: 显示文本} 字典
        """
        old_value = self.value()
        self._mapping = mapping.copy()
        self.blockSignals(True)
        self._populate_items()
        if old_value >= 0:
            idx = self.findData(old_value)
            if idx >= 0:
                self.setCurrentIndex(idx)
        self.blockSignals(False)

    def set_value(self, value: int) -> None:
        """设置当前选中项

        Args:
            value: 精神指令数值 key
        """
        self.blockSignals(True)
        idx = self.findData(value)
        if idx >= 0:
            self.setCurrentIndex(idx)
        self.blockSignals(False)

    def value(self) -> int:
        """获取当前选中项数值

        Returns:
            精神指令数值 key，无选中项返回 -1
        """
        idx = self.currentIndex()
        if idx >= 0:
            return self.itemData(idx)
        return -1

    def _populate_items(self) -> None:
        """按 mapping 填充下拉选项"""
        self.clear()
        for value, text in self._mapping.items():
            self.addItem(text, userData=value)

    # ========== 字体 ==========

    def set_dropdown_font(self, font: QFont) -> None:
        """设置下拉菜单项的字体 QSS

        Args:
            font: QFont 实例
        """
        self._view_qss = (
            "MenuActionListWidget#comboListWidget {"
            f"font-family: '{font.family()}' !important;"
            f"font-size: {font.pixelSize()}px !important;"
            "}"
        )

    def apply_font(self, font: QFont | dict) -> None:
        """设置下拉框字体

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
        self.setFont(font)

    def resetUI(self) -> None:
        """从全局配置刷新字体（含下拉菜单）"""
        font = getFont()
        setFont(self)
        self.set_dropdown_font(font)

    # ========== 下拉菜单（注入字体 QSS） ==========

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

        # ========== 追加字体 QSS ==========

        if self._view_qss:
            existing = menu.view.styleSheet()
            menu.view.setStyleSheet(existing + "\n" + self._view_qss)

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

    # ========== 内部槽 ==========

    def _on_index_changed(self, index: int) -> None:
        """选中项变化时发射 valueChanged"""
        if index >= 0:
            self.valueChanged.emit(self.itemData(index))
