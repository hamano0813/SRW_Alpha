"""
机体列表子框架 - 机体表格 + 搜索过滤容器

包含 FixedTableView 和预留给未来搜索过滤控件的空间。
继承 ProxyFrame，自动传播 resetUI / translateUI 至子控件。

Classes:
    UnitFrame: 机体列表子框架
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHeaderView, QVBoxLayout

from gui.custom import fonts
from gui.custom.delegates import (
    MappingSpinDelegate,
    NumberSpinDelegate,
    SingleLineDelegate,
)
from gui.custom.enums import EnumData
from gui.custom.models import BaseTableModel
from gui.custom.widgets.proxy_frame import ProxyFrame
from gui.custom.views import FixedTableView


class UnitFrame(ProxyFrame):
    """机体列表子框架 - 表格显示 + 搜索过滤容器

    封装 FixedTableView，对外暴露 set_field / set_data / set_title 和 sClicked 信号。
    下方预留空间用于后续搜索过滤控件。
    折叠/展开列时自动动画自身宽度，带动右侧面板平滑腾出空间。
    """

    sClicked = Signal(int, BaseTableModel)

    def __init__(self, parent=None):
        """初始化机体列表子框架

        Args:
            parent: 父 QWidget
        """
        super().__init__(parent)

        # ========== 机体表格 ==========

        self._robot_view = FixedTableView()
        self._robot_view.sClicked.connect(self.sClicked.emit)

        # ========== 模型字体与对齐 ==========

        _model = self._robot_view.source_model()
        _model.set_font({0: fonts.JP_FONT})
        _model.set_alignments(
            {
                1: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                2: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                3: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                4: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                5: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                6: Qt.AlignmentFlag.AlignCenter,
                7: Qt.AlignmentFlag.AlignCenter,
                8: Qt.AlignmentFlag.AlignCenter,
                9: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                10: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            }
        )

        # ========== 委托编辑器 ==========

        self._name_delegate = SingleLineDelegate(font=fonts.JP_FONT, parent=self._robot_view)
        self._robot_view.setItemDelegateForColumn(0, self._name_delegate)

        # ========== 数值列：纯键盘输入，无按钮 ==========

        self._hp_delegate = NumberSpinDelegate(value_range=(0, 65535), show_buttons=False, parent=self._robot_view)
        self._robot_view.setItemDelegateForColumn(1, self._hp_delegate)

        self._en_delegate = NumberSpinDelegate(value_range=(50, 400), show_buttons=False, parent=self._robot_view)
        self._robot_view.setItemDelegateForColumn(2, self._en_delegate)

        self._mobility_delegate = NumberSpinDelegate(value_range=(40, 200), show_buttons=False, parent=self._robot_view)
        self._robot_view.setItemDelegateForColumn(3, self._mobility_delegate)

        self._armor_delegate = NumberSpinDelegate(value_range=(100, 4000), show_buttons=False, parent=self._robot_view)
        self._robot_view.setItemDelegateForColumn(4, self._armor_delegate)

        self._limit_delegate = NumberSpinDelegate(value_range=(200, 999), show_buttons=False, parent=self._robot_view)
        self._robot_view.setItemDelegateForColumn(5, self._limit_delegate)

        # 步进列：有按钮，键盘只读
        self._slot_delegate = NumberSpinDelegate(value_range=(1, 4), show_buttons=True, parent=self._robot_view)
        self._robot_view.setItemDelegateForColumn(7, self._slot_delegate)
        self._move_delegate = NumberSpinDelegate(value_range=(3, 9), show_buttons=True, parent=self._robot_view)
        self._robot_view.setItemDelegateForColumn(8, self._move_delegate)

        _enum = EnumData()
        self._size_delegate = MappingSpinDelegate(mapping=_enum.ROBOT["SIZE"], parent=self._robot_view)
        self._robot_view.setItemDelegateForColumn(6, self._size_delegate)

        # ========== 资金列：无按钮 ==========

        self._rep_delegate = NumberSpinDelegate(value_range=(0, 65535), show_buttons=False, parent=self._robot_view)
        self._robot_view.setItemDelegateForColumn(9, self._rep_delegate)

        self._cost_delegate = NumberSpinDelegate(value_range=(0, 65535), show_buttons=False, parent=self._robot_view)
        self._robot_view.setItemDelegateForColumn(10, self._cost_delegate)

        # ========== 默认列宽 ==========

        self._robot_view.set_column_width([200] + [96] * 10)
        self._robot_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        # ========== 布局 ==========

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._robot_view)

        self.setLayout(layout)

    # ========== 公开接口 ==========

    @property
    def robot_view(self) -> FixedTableView:
        """获取内部表格视图

        Returns:
            FixedTableView 实例
        """
        return self._robot_view

    # ========== 翻译 ==========

    def translateUI(self):
        """刷新列标题与格式化函数"""
        self._robot_view.set_title(
            {
                self.tr("Robot name"): [self._name_delegate.format_display, self._name_delegate.parse_display],
                self.tr("Hit points"): [self._hp_delegate.format_display, self._hp_delegate.parse_display],
                self.tr("Energy"): [self._en_delegate.format_display, self._en_delegate.parse_display],
                self.tr("Mobility"): [self._mobility_delegate.format_display, self._mobility_delegate.parse_display],
                self.tr("Armor"): [self._armor_delegate.format_display, self._armor_delegate.parse_display],
                self.tr("Limit"): [self._limit_delegate.format_display, self._limit_delegate.parse_display],
                self.tr("Size"): [self._size_delegate.format_display, self._size_delegate.parse_display],
                self.tr("Parts slot"): [self._slot_delegate.format_display, self._slot_delegate.parse_display],
                self.tr("Movement"): [self._move_delegate.format_display, self._move_delegate.parse_display],
                self.tr("Repair cost"): [self._rep_delegate.format_display, self._rep_delegate.parse_display],
                self.tr("Cost"): [self._cost_delegate.format_display, self._cost_delegate.parse_display],
            }
        )
        if self._robot_view.column_widths:
            self._robot_view.set_column_width(self._robot_view.column_widths)

    # ========== 代理方法 ==========

    def set_field(self, fields) -> None:
        """设置字段映射，代理至内部表格视图

        Args:
            fields: FieldMapping 实例
        """
        self._robot_view.set_field(fields)

    def set_data(self, data: list[dict[str, Any]]) -> None:
        """装入列表数据，代理至内部表格视图

        Args:
            data: 行数据列表
        """
        self._robot_view.set_data(data)

    def set_title(self, titles: dict[str, list[Callable | None]]) -> None:
        """设置列标题与格式化函数，代理至内部表格视图

        set_title 会重置模型，导致列宽恢复默认，
        所以设完标题后重新应用预设列宽。

        Args:
            titles: {翻译后表头: [格式化函数, 反解析函数], ...}
        """
        self._robot_view.set_title(titles)
        if self._robot_view.column_widths:
            self._robot_view.set_column_width(self._robot_view.column_widths)
