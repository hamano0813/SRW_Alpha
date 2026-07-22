"""
消息列表子框架 - 消息表格容器

包含 FixedTableView 和配套的 MultiLineDelegate。
继承 ProxyFrame，自动传播 resetUI / translateUI 至子控件。

Classes:
    MsgFrame: 消息列表子框架
"""

from typing import Any, Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView, QVBoxLayout
from qfluentwidgets import TableItemDelegate

from gui.custom import fonts
from gui.widget import FixedTableView, MultiLineDelegate, ProxyFrame


class _SingleColumnDelegate(TableItemDelegate):
    """单列表格委托 — 一列时左右都画圆角

    qfluentwidgets 的 _drawBackground 在第 0 列只画左圆角、末列只画右圆角，
    但单列时第 0 列也是末列，右侧圆角缺失。本类补上右半圆角。
    """

    def _drawBackground(self, painter, option, index):
        """根据列位置决定圆角绘制区域：单列时左右都画圆角"""
        r = 5
        n = index.model().columnCount(index.parent())
        if n == 1:
            # 只有一列：同时画左右圆角
            rect = option.rect.adjusted(4, 0, -4, 0)
            painter.drawRoundedRect(rect, r, r)
        elif index.column() == 0:
            rect = option.rect.adjusted(4, 0, r + 1, 0)
            painter.drawRoundedRect(rect, r, r)
        elif index.column() == n - 1:
            rect = option.rect.adjusted(-r - 1, 0, -4, 0)
            painter.drawRoundedRect(rect, r, r)
        else:
            rect = option.rect.adjusted(-1, 0, 1, 0)
            painter.drawRect(rect)


class MsgFrame(ProxyFrame):
    """消息列表子框架 - 表格显示 + 搜索过滤容器

    封装 FixedTableView，对外暴露 set_field / set_data / set_title。
    """

    def __init__(self, parent=None):
        """初始化消息列表子框架

        Args:
            parent: 父 QWidget
        """
        super().__init__(parent)

        # ========== 消息表格 ==========

        self.message_view = FixedTableView()

        # ========== 模型字体 ==========

        self.message_view.source_model().set_font({0: fonts.JP_FONT})

        # ========== 委托编辑器 ==========

        self._name_delegate = MultiLineDelegate(font=fonts.JP_FONT, max_lines=3, parent=self.message_view)
        self.message_view.setItemDelegateForColumn(0, self._name_delegate)

        # 替换默认背景绘制的委托（单列时左右都画圆角）
        self.message_view.setItemDelegate(_SingleColumnDelegate(self.message_view))

        # ========== 默认列宽 ==========

        self.message_view.setMinimumWidth(480)
        self.message_view.horizontalHeader().setSectionsClickable(False)
        self.message_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.message_view.horizontalHeader().setStretchLastSection(False)
        self.message_view.verticalHeader().setDefaultSectionSize(66)
        self.message_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.message_view.set_alignments({0: Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop})

        # ========== 布局 ==========

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.message_view)

        self.setLayout(layout)

    # ========== 列宽自适应 ==========

    def resizeEvent(self, event):
        """视图宽度变化时自动更新第一列宽度 = 视口宽度 - 70"""
        super().resizeEvent(event)
        vw = self.message_view.width()
        self.message_view.setColumnWidth(0, max(200, vw - 70))

    # ========== 翻译 ==========

    def translateUI(self):
        """刷新列标题与格式化函数"""
        self.message_view.set_title({self.tr("Scenario Message"): [self._name_delegate.format_display, self._name_delegate.parse_display]})
        if self.message_view.column_widths:
            self.message_view.set_column_width(self.message_view.column_widths)

    # ========== 代理方法 ==========

    def set_field(self, fields) -> None:
        """设置字段映射，代理至内部表格视图

        Args:
            fields: FieldMapping 实例
        """
        self.message_view.set_field(fields)

    def set_data(self, data: list[dict[str, Any]]) -> None:
        """装入列表数据，代理至内部表格视图

        Args:
            data: 行数据列表
        """
        self.message_view.set_data(data)

    def set_title(self, titles: dict[str, list[Callable | None]]) -> None:
        """设置列标题与格式化函数，代理至内部表格视图

        Args:
            titles: {翻译后表头: [格式化函数, 反解析函数], ...}
        """
        self.message_view.set_title(titles)
        if self.message_view.column_widths:
            self.message_view.set_column_width(self.message_view.column_widths)
