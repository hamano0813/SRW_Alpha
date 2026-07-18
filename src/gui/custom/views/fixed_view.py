"""
固定行数表格视图 - 配合 FixedTableModel 使用

继承 BaseTableView，支持三态排序和单选行行为。
编辑器由外部 Delegate 提供，视图层不介入。

Classes:
    FixedTableView: 固定行数表格视图
"""

from PySide6.QtCore import QModelIndex, Qt, QRect, Signal
from PySide6.QtGui import QPainter, QPainterPath
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QStyle, QStyleOptionHeader

from gui.custom import fonts
from gui.custom.models.fixed_model import FixedTableModel

from .base_view import BaseTableView


class _SortHeader(QHeaderView):
    """自定义表头 — 禁用内置排序箭头，改为在标题文字正下方自绘小三角"""

    sortChanged = Signal(int, Qt.SortOrder)  # (section, order)

    _painting: bool = False  # 重入保护

    def __init__(self, parent=None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self._sort_section: int = -1
        self._sort_order: Qt.SortOrder = Qt.SortOrder.AscendingOrder

        self.setSectionsClickable(True)
        self.setSortIndicatorShown(False)  # 完全禁用内置箭头
        self.sectionClicked.connect(self._on_clicked)

    # ========== 三态排序 ==========

    def _on_clicked(self, section: int):
        """点击表头循环切换：无排序 → 正序 → 逆序 → 无排序

        Args:
            section: 被点击的列号
        """
        if self._sort_section != section:
            self._sort_section = section
            self._sort_order = Qt.SortOrder.AscendingOrder
        elif self._sort_order == Qt.SortOrder.AscendingOrder:
            self._sort_order = Qt.SortOrder.DescendingOrder
        else:
            self._sort_section = -1
            self._sort_order = Qt.SortOrder.AscendingOrder

        self.sortChanged.emit(self._sort_section, self._sort_order)
        self.viewport().update()

    # ========== 绘图 ==========

    def paintSection(self, painter: QPainter, rect: QRect, logicalIndex: int) -> None:
        """先让 QSS 正常绘制背景 + 标题文字，再在文字下方叠加排序三角

        Args:
            painter: 绘图器
            rect: 绘制区域
            logicalIndex: 列逻辑索引
        """
        if self._painting:
            return
        self._painting = True
        try:
            # ---- 1) QSS 正常绘制（背景 + 标题，无内置箭头） ----
            super().paintSection(painter, rect, logicalIndex)

            # ---- 2) 若本列是排序列，在文字下方绘小三角 ----
            if self._sort_section == logicalIndex:
                # 获取标题文字区域
                opt = QStyleOptionHeader()
                opt.initFrom(self)
                opt.rect = rect
                opt.section = logicalIndex

                label_rect = self.style().subElementRect(
                    QStyle.SubElement.SE_HeaderLabel, opt, self)

                # 三角尺寸
                aw, ah = 8, 5
                cx = label_rect.center().x()
                by = label_rect.bottom() - 1  # 紧贴文字底部

                painter.save()
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setPen(Qt.PenStyle.NoPen)
                color = opt.palette.color(opt.palette.ColorRole.Text)
                painter.setBrush(color)

                if self._sort_order == Qt.SortOrder.AscendingOrder:
                    pts = [(cx, by - ah),
                           (cx + aw // 2, by),
                           (cx - aw // 2, by)]
                else:
                    pts = [(cx, by),
                           (cx + aw // 2, by - ah),
                           (cx - aw // 2, by - ah)]

                path = QPainterPath()
                path.moveTo(*pts[0])
                for pt in pts[1:]:
                    path.lineTo(*pt)
                path.closeSubpath()
                painter.drawPath(path)
                painter.restore()
        finally:
            self._painting = False


class FixedTableView(BaseTableView):
    """固定行数表格视图 - 三态排序 + 单选行

    内部持有 FixedTableModel 实例，UI 层通过本视图间接操作模型。
    """

    def __init__(self, parent=None):
        """初始化固定表格视图，自动创建内部模型

        Args:
            parent: 父 QWidget
        """
        model = FixedTableModel()
        model.set_font({
            0: fonts.JP_FONT,
            1: fonts.EN_FONT, 2: fonts.EN_FONT, 3: fonts.EN_FONT,
            4: fonts.EN_FONT, 5: fonts.EN_FONT, 6: fonts.EN_FONT,
            7: fonts.EN_FONT, 8: fonts.EN_FONT,
        })
        model.set_alignments({
            1: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            2: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            3: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            4: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            5: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            6: Qt.AlignmentFlag.AlignCenter,
            7: Qt.AlignmentFlag.AlignCenter,
            8: Qt.AlignmentFlag.AlignCenter,
        })
        super().__init__(model, parent)

        # ========== 自定义表头 ==========

        old_header = self.horizontalHeader()
        stretch = old_header.stretchLastSection()

        sort_header = _SortHeader(self)
        self.setHorizontalHeader(sort_header)
        sort_header.setHighlightSections(False)
        sort_header.setStretchLastSection(stretch)
        sort_header.setStyleSheet(self.HORIZONTAL_QSS)
        # 强制重新 polish，使 qfluentwidgets 的 QSS 应用到新表头
        sort_header.style().unpolish(sort_header)
        sort_header.style().polish(sort_header)
        sort_header.sortChanged.connect(self._on_sort_changed)

        # ========== 行交互 ==========

        self.clicked.connect(self._single_click)

        # ========== 列宽配置 ==========

        self._widths: list[int] = []

    # ========== 列宽设置 ==========

    def set_column_width(self, widths: list[int]) -> None:
        """批量设置列宽，按顺序依次设定各列

        Args:
            widths: 每列的宽度值列表
        """
        self._widths = widths
        for col, width in enumerate(widths):
            self.setColumnWidth(col, width)

    # ========== 行定位 ==========

    def select_source_row(self, source_row: int) -> bool:
        """选中并滚动到指定的源行号（自动经代理模型转换）

        过滤状态下源行可能被隐藏，此时返回 False。

        Args:
            source_row: 源模型行号

        Returns:
            选中成功返回 True，行被过滤隐藏返回 False
        """
        if source_row < 0 or source_row >= self._model.rowCount():
            return False

        source_index = self._model.index(source_row, 0)
        proxy_index = self._proxy.mapFromSource(source_index)
        if not proxy_index.isValid():
            return False

        self.scrollTo(proxy_index, QAbstractItemView.ScrollHint.PositionAtCenter)
        self.setCurrentIndex(proxy_index)
        self.selectRow(proxy_index.row())
        return True

    # ========== 排序 ==========

    def _on_sort_changed(self, section: int, order: Qt.SortOrder):
        """表头排序状态变更时，通知代理模型排序

        Args:
            section: 排序列号，-1 表示清除排序
            order: 排序方向
        """
        if section >= 0:
            self._proxy.sort(section, order)
        else:
            self._proxy.sort(-1)

    # ========== 行交互 ==========

    def _single_click(self, index: QModelIndex) -> None:
        """单击行时发射 sClicked 信号

        通过 get_row_data 获取该行数据一并传出。

        Args:
            index: 被单击的单元格索引
        """
        if not index.isValid():
            return
        row_data = self.get_row_data(index.row())
        self.sClicked.emit(index.row(), row_data)
