"""
地图武器范围选择下拉框 - 带覆盖区域图标预览

每项显示一个 220x140 的缩略图，用红色高亮标出武器在地图上的覆盖范围。
MAP_RANGE 数据写死在此模块内。纯信号槽收发。

Classes:
    RangeCombo: 地图武器范围选择下拉框
"""

from PIL import Image, ImageDraw
from PySide6.QtCore import QPoint, QRectF, QSize, Qt, Signal
from PySide6.QtGui import QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QLabel, QPushButton, QStyle
from qfluentwidgets import ComboBox, FluentIcon, MenuAnimationType, RoundMenu, isDarkTheme, setFont
from qfluentwidgets.components.widgets.menu import MenuAnimationManager

_RANGE_PIX_W = 220
_RANGE_PIX_H = 140
_ARROW_W = 22
_MARGIN_V = 8
_LEFT_W = 12

MAP_RANGE: dict[int, tuple[tuple[int, int], ...]] = {
    0x00: ((2, 7), (3, 7), (3, 8), (4, 8), (5, 8), (5, 7)),
    0x01: ((1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6)),
    0x02: ((1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6)),
    0x03: ((1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6)),
    0x04: ((2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6), (11, 6)),
    0x05: ((2, 5), (3, 5), (4, 5), (5, 5),
           (1, 6), (2, 6), (3, 6), (4, 6), (5, 6),
           (2, 7), (3, 7), (4, 7), (5, 7)),
    0x06: ((1, 5), (2, 5), (3, 5), (4, 5),
           (1, 6), (2, 6), (3, 6), (4, 6), (5, 6),
           (1, 7), (2, 7), (3, 7), (4, 7)),
    0x07: ((1, 5), (2, 5), (3, 5), (4, 5), (5, 5),
           (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6),
           (1, 7), (2, 7), (3, 7), (4, 7), (5, 7)),
    0x08: ((2, 5), (3, 5), (4, 5), (5, 5), (6, 5),
           (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6),
           (2, 7), (3, 7), (4, 7), (5, 7), (6, 7)),
    0x09: ((2, 5), (3, 5),
           (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6),
           (2, 7), (3, 7)),
    0x0A: ((1, 5), (2, 5), (3, 5), (4, 5),
           (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6),
           (1, 7), (2, 7), (3, 7), (4, 7)),
    0x0B: ((3, 4), (4, 4), (5, 4),
           (2, 5), (3, 5), (4, 5), (5, 5),
           (1, 6), (2, 6), (3, 6), (4, 6), (5, 6),
           (2, 7), (3, 7), (4, 7), (5, 7),
           (3, 8), (4, 8), (5, 8)),
    0x0C: ((3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5),
           (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6), (10, 6),
           (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7)),
    0x0D: ((1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5),
           (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6),
           (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7)),
    0x0E: ((1, 4), (2, 4), (3, 4),
           (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5),
           (1, 6), (2, 6), (3, 6),
           (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7),
           (1, 8), (2, 8), (3, 8)),
    0x0F: ((4, 4),
           (3, 5), (4, 5),
           (2, 6), (3, 6), (4, 6),
           (3, 7), (4, 7),
           (4, 8)),
    0x10: ((5, 2),
           (4, 3), (5, 3),
           (3, 4), (4, 4), (5, 4),
           (2, 5), (3, 5), (4, 5), (5, 5),
           (1, 6), (2, 6), (3, 6), (4, 6), (5, 6),
           (2, 7), (3, 7), (4, 7), (5, 7),
           (3, 8), (4, 8), (5, 8),
           (4, 9), (5, 9),
           (5, 10)),
    0x11: ((5, 3), (6, 3),
           (3, 4), (4, 4),
           (1, 5), (2, 5),
           (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6),
           (1, 7), (2, 7),
           (3, 8), (4, 8),
           (5, 9), (6, 9)),
    0x12: ((1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5),
           (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6),
           (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7)),
    0x13: ((3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (9, 2),
           (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3),
           (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (9, 4),
           (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (9, 5),
           (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6),
           (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7), (9, 7),
           (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8), (8, 8), (9, 8),
           (3, 9), (4, 9), (5, 9), (6, 9), (7, 9), (8, 9), (9, 9),
           (3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10)),
    0x14: ((1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2),
           (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3),
           (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4),
           (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5),
           (1, 6), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (8, 6), (9, 6),
           (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7), (8, 7),
           (1, 8), (2, 8), (3, 8), (4, 8), (5, 8), (6, 8), (7, 8), (8, 8),
           (1, 9), (2, 9), (3, 9), (4, 9), (5, 9), (6, 9), (7, 9),
           (1, 10), (2, 10), (3, 10), (4, 10), (5, 10), (6, 10), (7, 10)),
    0x15: ((1, 4), (2, 4), (3, 4),
           (1, 5), (2, 5), (3, 5), (4, 5),
           (1, 6), (2, 6), (3, 6), (4, 6), (5, 6),
           (1, 7), (2, 7), (3, 7), (4, 7),
           (1, 8), (2, 8), (3, 8)),
}


def _render_range_pixmap(rect_list: tuple[tuple[int, int], ...], key: int | None = None,
                         text_color: str = "white") -> QPixmap:
    """将地图武器覆盖范围数据渲染为 QPixmap 图标

    Args:
        rect_list: 覆盖范围坐标列表
        key: 范围键值，不为 None 时在左上角绘制标签
        text_color: 标签文字颜色（如 "white"、"black"）
    """
    img = Image.new("RGBA", (131, 131), 0xA0804040)
    draw = ImageDraw.Draw(img)

    for line in range(14):
        draw.line([(0, line * 10), (130, line * 10)], fill="black", width=1)
        draw.line([(line * 10, 0), (line * 10, 130)], fill="black", width=1)

    draw.rectangle(((1, 61), (9, 69)), fill="gold")

    for rect in rect_list:
        x0 = 10 * rect[0] + 1
        y0 = 10 * rect[1] + 1
        draw.rectangle(((x0, y0), (x0 + 8, y0 + 8)), fill="red")

    rotated = img.rotate(45, resample=Image.BICUBIC, expand=True)
    resized = rotated.resize((220, 140))

    if key is not None:
        label = f"[0x{key:02X}]"
        draw2 = ImageDraw.Draw(resized)
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("segoeuib.ttf", 14)
        except (OSError, ImportError):
            font = ImageFont.load_default()
        draw2.text((3, 3), label, fill=text_color, font=font)

    return resized.toqpixmap()


class _RangeItemWidget(QLabel):
    """下拉菜单项 — 显示 220x140 范围预览图"""

    clicked = Signal(int)

    def __init__(self, pixmap: QPixmap, index: int):
        super().__init__()
        self._idx = index
        self.setPixmap(pixmap)
        self.setFixedSize(_RANGE_PIX_W, _RANGE_PIX_H)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, e):
        self.clicked.emit(self._idx)
        super().mousePressEvent(e)


class RangeCombo(ComboBox):
    """地图武器范围选择下拉框 - 带覆盖区域图标预览"""

    valueChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaxVisibleItems(3)

        tc = "white" if isDarkTheme() else "black"
        for key in sorted(MAP_RANGE):
            pixmap = _render_range_pixmap(MAP_RANGE[key], key, text_color=tc)
            self.addItem("", QIcon(pixmap), userData=key)

        self.currentIndexChanged.connect(self._on_index_changed)

    # ========== 尺寸 ==========

    def sizeHint(self):
        return QSize(_RANGE_PIX_W + _LEFT_W + _ARROW_W + _MARGIN_V,
                     _RANGE_PIX_H + _MARGIN_V * 2)

    # ========== 数据接口 ==========

    def set_value(self, value: int) -> None:
        self.blockSignals(True)
        idx = self.findData(int(value))
        if idx >= 0:
            self.setCurrentIndex(idx)
        self.blockSignals(False)

    def value(self) -> int:
        idx = self.currentIndex()
        if idx >= 0:
            return self.itemData(idx)
        return -1

    # ========== 启用/禁用 ==========

    def setEnabled(self, enabled: bool) -> None:
        if enabled and self.count() <= 1:
            self.blockSignals(True)
            self.clear()
            tc = "white" if isDarkTheme() else "black"
            for key in sorted(MAP_RANGE):
                pixmap = _render_range_pixmap(MAP_RANGE[key], key, text_color=tc)
                self.addItem("", QIcon(pixmap), userData=key)
            self.blockSignals(False)
        elif not enabled and self.count() > 1:
            self.blockSignals(True)
            self.clear()
            self.blockSignals(False)
        super().setEnabled(enabled)

    # ========== 字体 ==========

    def apply_font(self, font: QFont | dict) -> None:
        if isinstance(font, dict):
            qfont = QFont()
            for k in ("family", "size", "weight", "italic"):
                v = font.get(k)
                if v:
                    getattr(qfont, f"set{k.capitalize()}")(v)
            font = qfont
        self.setFont(font)

    def resetUI(self) -> None:
        """切换主题时刷新字体 + 替换文字颜色适配的预览图"""
        setFont(self)
        old_val = self.value()
        tc = "white" if isDarkTheme() else "black"
        self.blockSignals(True)
        self.clear()
        for key in sorted(MAP_RANGE):
            pixmap = _render_range_pixmap(MAP_RANGE[key], key, text_color=tc)
            self.addItem("", QIcon(pixmap), userData=key)
        if old_val >= 0:
            idx = self.findData(old_val)
            if idx >= 0:
                self.setCurrentIndex(idx)
        self.blockSignals(False)

    # ========== 按钮绘制 ==========

    def paintEvent(self, e):
        QPushButton.paintEvent(self, e)
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.RenderHint.Antialiasing | QPainter.RenderHint.SmoothPixmapTransform)

        idx = self.currentIndex()
        if 0 <= idx < len(self.items):
            pix = self.items[idx].icon.pixmap(QSize(_RANGE_PIX_W, _RANGE_PIX_H))
            if pix and not pix.isNull():
                painter.drawPixmap(_LEFT_W, (self.height() - _RANGE_PIX_H) // 2,
                                   _RANGE_PIX_W, _RANGE_PIX_H, pix)

        if self.isHover:
            painter.setOpacity(0.75)
        elif self.isPressed:
            painter.setOpacity(0.65)

        rect = QRectF(self.width() - 22, self.height() / 2 - 5 + self.arrowAni.y, 10, 10)
        if isDarkTheme():
            FluentIcon.ARROW_DOWN.render(painter, rect)
        else:
            FluentIcon.ARROW_DOWN.render(painter, rect, fill="#646464")

    # ========== 下拉菜单 ==========

    def _showComboMenu(self):
        if not self.items:
            return

        menu = RoundMenu("", self)
        menu.view.setViewportMargins(0, 2, 0, 6)
        menu.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        menu.view.setObjectName("comboListWidget")
        menu.setMaxVisibleItems(self.maxVisibleItems())
        menu.view.setItemHeight(140)
        menu.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        menu.closedSignal.connect(self._onDropMenuClosed)
        menu.hBoxLayout.setContentsMargins(20, 4, 20, 4)
        self.dropMenu = menu

        for i, item in enumerate(self.items):
            pix = item.icon.pixmap(QSize(_RANGE_PIX_W, _RANGE_PIX_H))
            widget = _RangeItemWidget(pix, i)
            widget.clicked.connect(lambda idx, m=menu: self._on_range_item_clicked(idx, m))
            menu.addWidget(widget, selectable=True)

        menu.view.adjustSize()
        if menu.view.width() < self.width():
            menu.view.setMinimumWidth(self.width())
            menu.view.adjustSize()
        menu.adjustSize()

        below_pos = self.mapToGlobal(QPoint(0, self.height())) - QPoint(20, 0)
        above_pos = self.mapToGlobal(QPoint(0, 0)) - QPoint(20, 0)
        _, space_below = MenuAnimationManager.make(
            menu.view, MenuAnimationType.DROP_DOWN).availableViewSize(below_pos)

        if space_below >= menu.view.height():
            menu.view.adjustSize(below_pos, MenuAnimationType.DROP_DOWN)
            menu.adjustSize()
            menu.move(below_pos)
        else:
            menu.view.adjustSize(above_pos, MenuAnimationType.PULL_UP)
            menu.adjustSize()
            menu.move(above_pos.x(), above_pos.y() - menu.height())
        menu.show()

    def _on_range_item_clicked(self, index: int, menu) -> None:
        self.setCurrentIndex(index)
        menu.close()

    # ========== 内部槽 ==========

    def _on_index_changed(self, index: int) -> None:
        if index >= 0:
            self.valueChanged.emit(self.itemData(index))
