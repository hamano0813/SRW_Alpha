"""
固定行数表格视图 - 配合 FixedTableModel 使用

继承 BaseTableView，支持三态排序和单选行行为。
编辑器由外部 Delegate 提供，视图层不介入。

Classes:
    FixedTableView: 固定行数表格视图
"""

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QAbstractItemView

from gui.custom.models.fixed_model import FixedTableModel

from .base_view import BaseTableView


class FixedTableView(BaseTableView):
    """固定行数表格视图 - 三态排序 + 单选行"""

    def __init__(self, model: FixedTableModel, parent=None):
        """初始化固定表格视图

        Args:
            model: FixedTableModel 实例
            parent: 父 QWidget
        """
        super().__init__(model, parent)

        # ========== 三态排序 ==========

        self.horizontalHeader().sectionClicked.connect(self._on_header_clicked)
        self._sort_section = -1
        self._sort_order = Qt.SortOrder.AscendingOrder
        self.horizontalHeader().setSortIndicatorShown(True)
        self.horizontalHeader().setSortIndicator(-1, Qt.SortOrder.AscendingOrder)

        # ========== 行选择 ==========

        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.clicked.connect(self._single_click)

    # ========== 三态排序 ==========

    def _on_header_clicked(self, section: int):
        """点击表头循环切换：无排序 → 正序 → 逆序 → 无排序

        Args:
            section: 被点击的列号
        """
        if self._sort_section != section:
            # 新列：从正序开始
            self._proxy.sort(section, Qt.SortOrder.AscendingOrder)
            self._sort_section = section
            self._sort_order = Qt.SortOrder.AscendingOrder
        elif self._sort_order == Qt.SortOrder.AscendingOrder:
            # 同一列第二次点击：变为逆序
            self._proxy.sort(section, Qt.SortOrder.DescendingOrder)
            self._sort_order = Qt.SortOrder.DescendingOrder
        else:
            # 同一列第三次点击：清除排序
            self._proxy.sort(-1)
            self.horizontalHeader().setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
            self._sort_section = -1
            self._sort_order = Qt.SortOrder.AscendingOrder

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
