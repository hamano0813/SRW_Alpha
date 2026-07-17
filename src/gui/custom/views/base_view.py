"""
基础表格视图 - 封装 qfluentwidgets 的 TableView

继承 qfluentwidgets 的 TableView，提供行选中、双击等交互信号，
以及列宽自适应、排序、代理模型等通用方法。视图层负责用户交互，
数据层由 BaseTableModel 子类管理。

Classes:
    BaseTableView: 基础表格视图
"""

from tkinter import VERTICAL
from typing import Any, Callable, cast

from PySide6.QtCore import QSortFilterProxyModel, Signal
from PySide6.QtWidgets import QAbstractButton, QPushButton, QVBoxLayout
from qfluentwidgets import TableView, isDarkTheme

from gui.custom.fields import FieldMapping
from gui.custom.models.base_model import BaseTableModel


class BaseTableView(TableView):
    """基础表格视图 - 封装 qfluentwidgets TableView 的通用行为

    预备与 BaseTableModel 子类配合使用，以 set_model() 绑定模型后自动连接信号。
    """

    # ========== 交互信号 ==========

    sClicked = Signal(int, dict)  # 单击某行 (视图行号, 行数据)
    dClicked = Signal(int, dict)  # 双击某行 (视图行号, 行数据)
    widthChanged = Signal(int, int)

    HORIZONTAL_QSS = (
        "QHeaderView::section { border: none; font-size: 14px; font-weight: 800; }"
    )
    VERTICAL_QSS = "QHeaderView::section { border: none; font-size: 13px; }"
    CORNER_QSS = "QTableView QTableCornerButton::section { background-color: transparent; border: none; }"
    BUTTON_QSS = "QPushButton {{color: {color}; background-color: transparent; border: none; font-size: 20px; font-weight: 800;}}"

    def __init__(self, model: BaseTableModel, parent=None):
        """初始化表格视图，绑定模型并创建代理

        Args:
            model: BaseTableModel 子类实例
            parent: 父 QWidget
        """
        super().__init__(parent)

        # ========== 内部状态 ==========

        self._proxy: QSortFilterProxyModel = QSortFilterProxyModel()
        self._model: BaseTableModel = model
        self._proxy.setSourceModel(model)
        self.setModel(self._proxy)

        self.setSortingEnabled(False)

        # ========== 表头去边框 ==========
        self.verticalHeader().setStyleSheet(self.VERTICAL_QSS)
        self.horizontalHeader().setStyleSheet(self.HORIZONTAL_QSS)

        # ========== 角落折叠按钮 ==========

        self._corner_button = QPushButton("")
        self.setCornerButton(self._corner_button)
        self._corner_button.clicked.connect(self.hide_columns)

    # ========== 列折叠切换 ==========

    def hide_columns(self):
        """切换第 1 列之后所有列的显示/隐藏，并更新按钮文字"""
        if self._model.columnCount() <= 1:
            return

        for col_idx in range(1, self._model.columnCount()):
            hidden = self.isColumnHidden(col_idx)
            self.setColumnHidden(col_idx, not hidden)

        if not hidden:
            self._corner_button.setText("»")
        else:
            self._corner_button.setText("«")
        self.changed_hidden(hidden)

    def changed_hidden(self, hidden: bool):
        vh_width = self.verticalHeader().width()
        cols_width = self.columnWidth(0)
        if hidden:
            for col_idx in range(1, self._model.columnCount()):
                cols_width += self.columnWidth(col_idx)
        bd_width = 5
        target_width = vh_width + cols_width + bd_width
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

    # ========== 模型绑定 ==========

    def set_model(self, model: BaseTableModel) -> None:
        """替换绑定的源模型

        断开旧模型的选中信号，将新模型设为代理的源模型。

        Args:
            model: BaseTableModel 子类实例
        """
        # 先断开旧模型的信号，避免切换后重复触发
        old_sel = self.selectionModel()
        if old_sel is not None:
            try:
                old_sel.selectionChanged.disconnect()
            except TypeError, RuntimeError:
                pass

        self._model = model
        self._proxy.setSourceModel(model)

    def proxy_model(self) -> QSortFilterProxyModel:
        """获取代理模型引用

        Returns:
            QSortFilterProxyModel 实例
        """
        return self._proxy

    def source_model(self) -> BaseTableModel:
        """获取源模型引用

        Returns:
            绑定的 BaseTableModel 子类
        """
        return self._model

    def get_row_data(self, row: int) -> dict[str, Any]:
        """获取指定视图行的原始数据（自动转换代理行号 → 源行号）

        Args:
            row: 视图中的行号

        Returns:
            该行的数据 dict
        """
        row_idx = self._proxy.mapToSource(self._proxy.index(row, 0)).row()
        return self._model.get_row_data(row_idx)

    # ========== 数据读写 ==========

    def set_data(self, data: list[dict[str, Any]]) -> None:
        """向模型装入列表数据

        Args:
            data: 行数据列表，每项为 dict
        """
        self._model.set_data(data)
        if self._model.columnCount() > 1:
            self._corner_button.setText("«")

    def set_title(self, titles: dict[str, list[Callable | None]]) -> None:
        """设置列标题与格式化函数

        Args:
            titles: {翻译后表头: [格式化函数, 反解析函数], ...}
        """
        self._model.set_title(titles)

    def set_field(self, fields: FieldMapping) -> None:
        """设置字段映射查询器

        Args:
            fields: FieldMapping 实例
        """
        self._model.set_field(fields)

    def resetUI(self):
        """根据当前主题刷新角落按钮颜色"""
        if isDarkTheme():
            self._corner_button.setStyleSheet(self.BUTTON_QSS.format(color="#CBCBCB"))
        else:
            self._corner_button.setStyleSheet(self.BUTTON_QSS.format(color="#606060"))
