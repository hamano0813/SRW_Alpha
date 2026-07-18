"""
消息列表子框架 - 消息表格容器

包含 FixedTableView 和配套的 MultiLineDelegate。
继承 ProxyFrame，自动传播 resetUI / translateUI 至子控件。

Classes:
    MsgFrame: 消息列表子框架
"""

from typing import Any, Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHeaderView, QVBoxLayout

from gui.custom import fonts
from gui.custom.delegates import MultiLineDelegate
from gui.custom.proxy_frame import ProxyFrame
from gui.custom.views.fixed_view import FixedTableView


class MsgFrame(ProxyFrame):
    """消息列表子框架 - 表格显示 + 搜索过滤容器

    封装 FixedTableView，对外暴露 set_field / set_data / set_title 和 sClicked 信号。
    """

    sClicked = Signal(int, dict)

    def __init__(self, parent=None):
        """初始化消息列表子框架

        Args:
            parent: 父 QWidget
        """
        super().__init__(parent)

        # ========== 消息表格 ==========

        self._message_view = FixedTableView()
        self._message_view.sClicked.connect(self.sClicked.emit)

        # ========== 委托编辑器 ==========

        self._name_delegate = MultiLineDelegate(font=fonts.JP_FONT, parent=self._message_view)
        self._message_view.setItemDelegateForColumn(0, self._name_delegate)

        # ========== 默认列宽 ==========

        self._message_view.setMinimumWidth(480)
        self._message_view.horizontalHeader().setSectionsClickable(False)
        self._message_view.set_column_width([800])
        self._message_view.verticalHeader().setDefaultSectionSize(66)
        self._message_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self._message_view.horizontalHeader().setStretchLastSection(True)
        self._message_view.set_alignments({0: Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop})

        # ========== 布局 ==========

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._message_view)

        self.setLayout(layout)

    # ========== 翻译 ==========

    def translateUI(self):
        """刷新列标题与格式化函数"""
        self._message_view.set_title(
            {
                self.tr("message"): [self._name_delegate.format_display, self._name_delegate.parse_display],
            }
        )
        if self._message_view._widths:
            self._message_view.set_column_width(self._message_view._widths)

    # ========== 代理方法 ==========

    def set_field(self, fields) -> None:
        """设置字段映射，代理至内部表格视图

        Args:
            fields: FieldMapping 实例
        """
        self._message_view.set_field(fields)

    def set_data(self, data: list[dict[str, Any]]) -> None:
        """装入列表数据，代理至内部表格视图

        Args:
            data: 行数据列表
        """
        self._message_view.set_data(data)

    def set_title(self, titles: dict[str, list[Callable | None]]) -> None:
        """设置列标题与格式化函数，代理至内部表格视图

        Args:
            titles: {翻译后表头: [格式化函数, 反解析函数], ...}
        """
        self._message_view.set_title(titles)
        if self._message_view._widths:
            self._message_view.set_column_width(self._message_view._widths)
