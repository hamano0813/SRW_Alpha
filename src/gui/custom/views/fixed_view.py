"""
固定行数表格视图 - 配合 FixedTableModel 使用

继承 BaseTableView，支持三态排序和单选行行为。
编辑器由外部 Delegate 提供，视图层不介入。

Classes:
    FixedTableView: 固定行数表格视图
"""

from typing import Any, cast

from PySide6.QtCore import QModelIndex, QRect, Qt, Signal
from PySide6.QtGui import QPainter, QPainterPath
from PySide6.QtWidgets import (
    QAbstractButton,
    QAbstractItemView,
    QHeaderView,
    QPushButton,
    QStyle,
    QStyleOptionHeader,
    QVBoxLayout,
)
from qfluentwidgets import isDarkTheme

from gui.custom.models import FixedTableModel

from .base_view import BaseTableView


class _SortHeader(QHeaderView):
    """自定义表头 — 禁用内置排序箭头，改为在标题文字正下方自绘小三角"""

    sortChanged = Signal(int, Qt.SortOrder)  # (section, order)

    _painting: bool = False  # 重入保护

    def __init__(self, parent=None):
        """初始化自定义表头，禁用内置排序箭头"""
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

                label_rect = self.style().subElementRect(QStyle.SubElement.SE_HeaderLabel, opt, self)

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
                    pts = [(cx, by - ah), (cx + aw // 2, by), (cx - aw // 2, by)]
                else:
                    pts = [(cx, by), (cx + aw // 2, by - ah), (cx - aw // 2, by - ah)]

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

    # ========== 列折叠信号 ==========

    foldToggled = Signal(bool, int)  # (列已折叠?, 释放的像素宽度)
    widthChanged = Signal(int, int)

    CORNER_QSS = "QTableView QTableCornerButton::section { background-color: transparent; border: none; }"
    BUTTON_QSS = "QPushButton {{color: {color}; background-color: transparent; border: none; font-size: 20px; font-weight: 800;}}"

    def __init__(self, parent=None):
        """初始化固定表格视图，自动创建内部模型

        Args:
            parent: 父 QWidget
        """
        model = FixedTableModel()
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

        self.clicked.connect(self._single_click)

        # ========== 列宽配置 ==========

        self._widths: list[int] = []

        # ========== 角落折叠按钮 ==========

        self._corner_button = QPushButton("")
        self.setCornerButton(self._corner_button)
        self._corner_button.clicked.connect(self.hide_columns)

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

        代理行号经 proxy 映射为源模型行号后，与 model 引用一同传出。
        model 继承自 QObject，跨信号传递时不会复制。

        Args:
            index: 被单击的单元格索引
        """
        if not index.isValid():
            return
        source_row = self._proxy.mapToSource(self._proxy.index(index.row(), 0)).row()
        self.sClicked.emit(source_row, self._model)

    # ========== 列宽查询 ==========

    @property
    def column_widths(self) -> list[int]:
        """获取当前列宽配置

        Returns:
            列宽列表
        """
        return list(self._widths)

    # ========== 数据装入 ==========

    def set_data(self, data: list[dict[str, Any]]) -> None:
        """装入列表数据并更新角落按钮文字

        Args:
            data: 行数据列表，每项为 dict
        """
        self._model.set_data(data)
        if self._model.columnCount() > 1:
            self._corner_button.setText("«")

    # ========== 列折叠切换 ==========

    def hide_columns(self):
        """切换第 1 列之后所有列的显示/隐藏，并更新按钮文字"""
        if self._model.columnCount() <= 1:
            return

        for col_idx in range(1, self._model.columnCount()):
            hidden = self.isColumnHidden(col_idx)
            self.setColumnHidden(col_idx, not hidden)

        # hidden 是切换前的状态，取反得到当前状态
        folded = not hidden
        self._corner_button.setText("»" if folded else "«")
        self.changed_hidden(folded)

    def changed_hidden(self, folded: bool):
        """列折叠状态变更 — 计算折叠后宽度及释放空间

        Args:
            folded: True=列已折叠（仅显示第 0 列），False=全部展开
        """
        vh_width = self.verticalHeader().width()
        # 折叠后只保留第 0 列
        cols_width = self.columnWidth(0)
        bd_width = 10
        if not folded:
            # 展开状态：累加所有列
            for col_idx in range(1, self._model.columnCount()):
                cols_width += self.columnWidth(col_idx)
            bd_width = 5
        target_width = vh_width + cols_width + bd_width
        source_width = self.width()
        freed_width = source_width - target_width
        self.widthChanged.emit(source_width, target_width)
        self.foldToggled.emit(folded, freed_width)
        source_width = self.width()
        self.widthChanged.emit(source_width, target_width)

    def setCornerButton(self, corner: QAbstractButton):
        """将按钮嵌入内置 corner widget 中

        Args:
            corner: 要嵌入的 QAbstractButton
        """
        corner = cast(
            QAbstractButton,
            self.findChild(QAbstractButton, "qt_tableview_cornerbutton"),
        )
        corner.setContentsMargins(0, 0, 0, 0)
        corner.setStyleSheet(self.CORNER_QSS)
        layout = QVBoxLayout(corner)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._corner_button)

    def resetUI(self):
        """根据当前主题刷新角落按钮颜色"""
        if isDarkTheme():
            self._corner_button.setStyleSheet(self.BUTTON_QSS.format(color="#CBCBCB"))
        else:
            self._corner_button.setStyleSheet(self.BUTTON_QSS.format(color="#606060"))
