"""
固定行数表格视图 - 配合 FixedTableModel 使用

继承 BaseTableView，启用列头排序，配置单选行行为。
编辑器由外部 Delegate 提供，视图层不介入。

Classes:
    FixedTableView: 固定行数表格视图
"""

from PySide6.QtCore import QModelIndex
from PySide6.QtWidgets import QAbstractItemView

from gui.custom.models.fixed_model import FixedTableModel

from .base_view import BaseTableView


class FixedTableView(BaseTableView):
    """固定行数表格视图 - 支持排序与单选行

    构造时自动绑定 FixedTableModel 并启用点击列头排序。
    """

    def __init__(self, model: FixedTableModel, parent=None):
        """初始化固定表格视图

        Args:
            model: FixedTableModel 实例
            parent: 父 QWidget
        """
        super().__init__(model, parent)

        # 启用列头排序（BaseTableView 默认关闭）
        self.setSortingEnabled(True)

        # 单选行
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.clicked.connect(self._single_click)

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
