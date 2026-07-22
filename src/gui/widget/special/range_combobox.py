"""
RangeComboBox 地图武器范围选择下拉框 - 带覆盖区域图标预览

每项显示一个 220×140 的缩略图，用红色高亮标出武器在地图上的覆盖范围。
MAP_RANGE 数据写死在此模块内。

放置于 widgets/special/ 子包。

Classes:
    RangeComboBox: 地图武器范围选择下拉框
"""

import os
import sys

# 将 src 目录加入模块搜索路径，支持直接 python path/to/file.py 运行
_src = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if _src not in sys.path:
    sys.path.insert(0, _src)

from typing import Any

from PIL import Image, ImageDraw
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QComboBox, QVBoxLayout

from gui.widget.common import PanelEditor

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
    """将地图武器覆盖范围数据渲染为 QPixmap 图标

    Args:
        rect_list: 覆盖坐标列表，每项 (x, y)
        key:      可选，在图片左上角绘制此标识文字

    Returns:
        220×140 的 QPixmap，45° 俯视棋盘格
    """
    img = Image.new("RGBA", (131, 131), 0xA0804040)
    draw = ImageDraw.Draw(img)

    # 棋盘网格线
    for line in range(14):
        draw.line([(0, line * 10), (130, line * 10)], fill="black", width=1)
        draw.line([(line * 10, 0), (line * 10, 130)], fill="black", width=1)

    # 自机中心（金色）
    draw.rectangle(((1, 61), (9, 69)), fill="gold")

    # 覆盖范围（红色）
    for rect in rect_list:
        x0 = 10 * rect[0] + 1
        y0 = 10 * rect[1] + 1
        draw.rectangle(((x0, y0), (x0 + 8, y0 + 8)), fill="red")

    # 45° 旋转 + 缩放到 220×140
    rotated = img.rotate(45, resample=Image.BICUBIC, expand=True)
    resized = rotated.resize((220, 140))

    # 在左上角叠加标识文字
    if key is not None:
        label = f"[0x{key:02X}]"
        draw2 = ImageDraw.Draw(resized)
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("segoeuib.ttf", 14)
        except (OSError, ImportError):
            font = ImageFont.load_default()
        # 加粗白色文字，无描边
        draw2.text((3, 3), label, fill="white", font=font)

    return resized.toqpixmap()


class RangeComboBox(PanelEditor):
    """地图武器范围选择下拉框 - 带覆盖区域图标预览

    每项显示一个 220×140 的棋盘点阵图，红点标出覆盖范围。
    继承 PanelEditor，通过 set_model/set_row 读写数据。
    """

    def __init__(self, field: str = "", parent=None):
        """初始化地图武器范围选择下拉框

        Args:
            field:  数据字典中对应的键名
            parent: 父 QWidget
        """
        super().__init__(field, parent)

        self._combo = QComboBox(self)
        self._combo.setIconSize(QSize(220, 140))
        self._combo.setMaxVisibleItems(5)

        # 预生成图标 + 填充选项
        self._key_list: list[int] = []
        for key in sorted(MAP_RANGE):
            self._key_list.append(key)
            pixmap = _render_range_pixmap(MAP_RANGE[key], key)
            self._combo.addItem(QIcon(pixmap), "", key)

        # 选择变更 → 写回数据
        self._combo.currentIndexChanged.connect(self._on_index_changed)

        # ========== 布局 ==========

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._combo)

    # ========== PanelEditor 数据协议 ==========

    def set_row(self, row: int) -> None:
        """切换行并刷新下拉选中项"""
        super().set_row(row)

    def format_value(self) -> None:
        """将 self._value 同步到下拉框选中项"""
        if self._value is None:
            self._combo.setCurrentIndex(-1)
            return
        try:
            idx = self._key_list.index(int(self._value))
        except (ValueError, TypeError):
            idx = -1
        self._combo.blockSignals(True)
        self._combo.setCurrentIndex(idx)
        self._combo.blockSignals(False)

    # ========== 启用/禁用（清空/恢复选项） ==========

    def setEnabled(self, enabled: bool) -> None:
        """禁用时保留占位项维持高度，恢复时重新填充

        Args:
            enabled: True=可用，False=禁用
        """
        if enabled and self._combo.count() <= 1:
            # 恢复选项
            self._key_list = []
            self._combo.blockSignals(True)
            self._combo.clear()
            for key in sorted(MAP_RANGE):
                self._key_list.append(key)
                pixmap = _render_range_pixmap(MAP_RANGE[key], key)
                self._combo.addItem(QIcon(pixmap), "", key)
            self._combo.blockSignals(False)
        elif not enabled and self._combo.count() > 1:
            # 清空选项，保留一个占位项维持高度
            self._combo.blockSignals(True)
            self._combo.clear()
            self._key_list = []
            dummy = Image.new("RGBA", (220, 140), (0, 0, 0, 0))
            self._combo.addItem(QIcon(dummy.toqpixmap()), "")
            self._combo.blockSignals(False)
        super().setEnabled(enabled)

    # ========== 字体 ==========

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
        """刷新字体"""
        font = self.font()
        self._combo.setFont(font)

    # ========== 内部槽 ==========

    def _on_index_changed(self, index: int) -> None:
        """下拉选择变更时写回数据

        Args:
            index: 当前选中项索引，-1 表示无选中
        """
        if index < 0:
            self._value = None
        else:
            self._value = self._key_list[index]
        self._emit_data_changed()


# =============================================================================
# 原地测试
# =============================================================================

if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget

    app = QApplication(sys.argv)

    w = QMainWindow()
    w.setWindowTitle("RangeComboBox 测试")
    w.setCentralWidget(QWidget())
    w.setGeometry(100, 100, 400, 200)

    combo = RangeComboBox("mrng", w)
    # 模拟数据
    combo._value = 0x05
    combo.format_value()
    combo.setParent(w.centralWidget())

    # 布局
    layout = QVBoxLayout(w.centralWidget())
    layout.addWidget(combo)
    layout.addStretch()

    # 测试回调
    def on_changed(field):
        print(f"[TEST] dataChanged: field={field}, value={combo._value:#04x}")

    combo.dataChanged.connect(on_changed)

    w.show()
    sys.exit(app.exec())
