"""
驾驶员表格子框架

包含 FixedTableView，显示驾驶员列表。
参照 unit_frame.py 的模式实现。

Classes:
    PilotTable: 驾驶员表格子框架
"""

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHeaderView, QVBoxLayout

from gui.custom import fonts
from gui.widget import (
    BaseTableModel,
    FixedTableView,
    NumberSpinDelegate,
    ProxyFrame,
    SingleLineDelegate,
)


class PilotTable(ProxyFrame):
    """驾驶员表格子框架 - 表格显示 + 搜索过滤容器

    封装 FixedTableView，对外暴露 set_field / set_data 和 sClicked 信号。
    """

    sClicked = Signal(int, BaseTableModel)

    def __init__(self, parent=None):
        """初始化驾驶员表格子框架

        Args:
            parent: 父 QWidget
        """
        super().__init__(parent)

        # ========== 驾驶员表格 ==========

        self._pilot_view = FixedTableView()
        self._pilot_view.sClicked.connect(self.sClicked.emit)

        # ========== 模型字体与对齐 ==========

        _model = self._pilot_view.source_model()
        _model.set_font({0: fonts.JP_FONT})
        _model.set_alignments(
            {
                1: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                2: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                3: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                4: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                5: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                6: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            }
        )

        # ========== 委托编辑器 ==========

        self._name_delegate = SingleLineDelegate(font=fonts.JP_FONT, parent=self._pilot_view)
        self._pilot_view.setItemDelegateForColumn(0, self._name_delegate)

        # 数值列：纯键盘输入，无按钮
        self._cqb_delegate = NumberSpinDelegate(value_range=(0, 999), show_buttons=False, parent=self._pilot_view)
        self._pilot_view.setItemDelegateForColumn(1, self._cqb_delegate)

        self._rng_delegate = NumberSpinDelegate(value_range=(0, 999), show_buttons=False, parent=self._pilot_view)
        self._pilot_view.setItemDelegateForColumn(2, self._rng_delegate)

        self._evd_delegate = NumberSpinDelegate(value_range=(0, 999), show_buttons=False, parent=self._pilot_view)
        self._pilot_view.setItemDelegateForColumn(3, self._evd_delegate)

        self._hit_delegate = NumberSpinDelegate(value_range=(0, 999), show_buttons=False, parent=self._pilot_view)
        self._pilot_view.setItemDelegateForColumn(4, self._hit_delegate)

        self._rxn_delegate = NumberSpinDelegate(value_range=(0, 999), show_buttons=False, parent=self._pilot_view)
        self._pilot_view.setItemDelegateForColumn(5, self._rxn_delegate)

        self._skl_delegate = NumberSpinDelegate(value_range=(0, 999), show_buttons=False, parent=self._pilot_view)
        self._pilot_view.setItemDelegateForColumn(6, self._skl_delegate)

        # ========== 默认列宽 ==========

        self._pilot_view.set_column_width([125] + [90] * 6)
        self._pilot_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self._pilot_view.verticalHeader().setFixedWidth(45)

        # 显示网格以查看列宽
        self._pilot_view.setShowGrid(True)

        # 默认隐藏折叠按钮
        self._pilot_view._corner_button.setVisible(False)

        # ========== 布局 ==========

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._pilot_view)

        self.setLayout(layout)

    # ========== 公开接口 ==========

    @property
    def pilot_view(self) -> FixedTableView:
        """获取内部表格视图

        Returns:
            FixedTableView 实例
        """
        return self._pilot_view

    # ========== 翻译 ==========

    def translateUI(self):
        """刷新列标题与格式化函数"""
        self._pilot_view.set_title(
            {
                self.tr("Nickname"): [self._name_delegate.format_display, self._name_delegate.parse_display],
                self.tr("Combat"): [self._cqb_delegate.format_display, self._cqb_delegate.parse_display],
                self.tr("Ranged"): [self._rng_delegate.format_display, self._rng_delegate.parse_display],
                self.tr("Evasion"): [self._evd_delegate.format_display, self._evd_delegate.parse_display],
                self.tr("Accuracy"): [self._hit_delegate.format_display, self._hit_delegate.parse_display],
                self.tr("Reaction"): [self._rxn_delegate.format_display, self._rxn_delegate.parse_display],
                self.tr("Skill"): [self._skl_delegate.format_display, self._skl_delegate.parse_display],
            }
        )
        if self._pilot_view.column_widths:
            self._pilot_view.set_column_width(self._pilot_view.column_widths)

    # ========== 代理方法 ==========

    def set_field(self, fields) -> None:
        """设置字段映射，代理至内部表格视图

        Args:
            fields: FieldMapping 实例
        """
        self._pilot_view.set_field(fields)

    def set_data(self, data: list[dict[str, Any]]) -> None:
        """装入列表数据，代理至内部表格视图

        Args:
            data: 行数据列表
        """
        self._pilot_view.set_data(data)
