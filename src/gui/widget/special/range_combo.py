"""
地图武器范围选择下拉框 - 带覆盖区域图标预览

每项显示一个 220×140 的缩略图，用红色高亮标出武器在地图上的覆盖范围。
MAP_RANGE 数据写死在此模块内。纯信号槽收发。

Classes:
    RangeCombo: 地图武器范围选择下拉框
"""

from PIL import Image, ImageDraw
from PySide6.QtCore import QSize, Signal
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QComboBox

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


def _render_range_pixmap(rect_list: tuple[tuple[int, int], ...], key: int | None = None) -> QPixmap:
    """将地图武器覆盖范围数据渲染为 QPixmap 图标"""
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
        draw2.text((3, 3), label, fill="white", font=font)

    return resized.toqpixmap()


class RangeCombo(QComboBox):
    """地图武器范围选择下拉框 - 带覆盖区域图标预览

    继承 QComboBox，每项显示一个 220×140 的棋盘点阵图。
    选中后发射 valueChanged(int)。
    """

    valueChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIconSize(QSize(220, 140))
        self.setMaxVisibleItems(5)

        self._key_list: list[int] = []
        for key in sorted(MAP_RANGE):
            self._key_list.append(key)
            pixmap = _render_range_pixmap(MAP_RANGE[key], key)
            self.addItem(QIcon(pixmap), "", key)

        self.currentIndexChanged.connect(self._on_index_changed)

    # ========== 数据接口 ==========

    def set_value(self, value: int) -> None:
        """设置当前选中项"""
        try:
            idx = self._key_list.index(int(value))
        except (ValueError, TypeError):
            idx = -1
        self.blockSignals(True)
        self.setCurrentIndex(idx)
        self.blockSignals(False)

    def value(self) -> int:
        """获取当前选中值"""
        idx = self.currentIndex()
        if idx >= 0:
            return self._key_list[idx]
        return -1

    # ========== 启用/禁用 ==========

    def setEnabled(self, enabled: bool) -> None:
        """禁用时保留占位项维持高度，恢复时重新填充"""
        if enabled and self.count() <= 1:
            self._key_list = []
            self.blockSignals(True)
            self.clear()
            for key in sorted(MAP_RANGE):
                self._key_list.append(key)
                pixmap = _render_range_pixmap(MAP_RANGE[key], key)
                self.addItem(QIcon(pixmap), "", key)
            self.blockSignals(False)
        elif not enabled and self.count() > 1:
            self.blockSignals(True)
            self.clear()
            self._key_list = []
            dummy = Image.new("RGBA", (220, 140), (0, 0, 0, 0))
            self.addItem(QIcon(dummy.toqpixmap()), "")
            self.blockSignals(False)
        super().setEnabled(enabled)

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
        """刷新字体"""
        self.setFont(self.font())

    # ========== 内部槽 ==========

    def _on_index_changed(self, index: int) -> None:
        """下拉选择变更时发射 valueChanged"""
        if index < 0:
            return
        self.valueChanged.emit(self._key_list[index])
