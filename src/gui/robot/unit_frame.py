"""
机体列表子框架 - 机体表格 + 搜索过滤容器

包含 FixedTableView 和预留给未来搜索过滤控件的空间。
继承 ProxyFrame，自动传播 resetUI / translateUI 至子控件。

Classes:
    UnitFrame: 机体列表子框架
"""

from typing import Any, Callable

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Signal
from PySide6.QtWidgets import QVBoxLayout

from gui.custom import fonts
from gui.custom.delegates import LineTextDelegate
from gui.custom.proxy_frame import ProxyFrame
from gui.custom.views.fixed_view import FixedTableView


class UnitFrame(ProxyFrame):
    """机体列表子框架 - 表格显示 + 搜索过滤容器

    封装 FixedTableView，对外暴露 set_field / set_data / set_title 和 sClicked 信号。
    下方预留空间用于后续搜索过滤控件。
    折叠/展开列时自动动画自身宽度，带动右侧面板平滑腾出空间。
    """

    sClicked = Signal(int, dict)

    def __init__(self, parent=None):
        """初始化机体列表子框架

        Args:
            parent: 父 QWidget
        """
        super().__init__(parent)

        # ========== 机体表格 ==========

        self._robot_view = FixedTableView()
        self._robot_view.sClicked.connect(self.sClicked.emit)

        # ========== 第一列委托编辑器 ==========

        self._name_delegate = LineTextDelegate(font=fonts.JP_FONT, parent=self._robot_view)
        self._robot_view.setItemDelegateForColumn(0, self._name_delegate)

        # ========== 宽度折叠动画 ==========

        self._width_anim = QPropertyAnimation(self, b"maximumWidth")
        self._width_anim.setDuration(250)
        self._width_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._robot_view.widthChanged.connect(self._on_width_changed)

        # ========== 默认列宽 ==========

        self._robot_view.set_column_width([200] + [84] * 8 + [120])

        # ========== 布局 ==========

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._robot_view)

        self.setLayout(layout)

    # ========== 动画 ==========

    def _on_width_changed(self, source: int, target: int):
        """平滑动画自身宽度至目标值

        锁定当前宽度为上限，再由动画过渡到 target，
        让 QHBoxLayout 重新分配多余空间给右侧面板。

        Args:
            source: 变化前宽度（未使用，用 self.width() 取实时值）
            target: 内容所需的目标宽度
        """
        self._width_anim.stop()
        self.setMaximumWidth(self.width())
        self._width_anim.setStartValue(self.width())
        self._width_anim.setEndValue(target)
        self._width_anim.start()

    # ========== 翻译 ==========

    def translateUI(self):
        """刷新列标题与格式化函数"""
        self._robot_view.set_title(
            {
                self.tr("robot name"): [self._name_delegate.format_display, self._name_delegate.parse_display],
                self.tr("hit points"): [lambda x: x, lambda x: x],
                self.tr("energy"): [lambda x: x, lambda x: x],
                self.tr("mobility"): [lambda x: x, lambda x: x],
                self.tr("armor"): [lambda x: x, lambda x: x],
                self.tr("limit"): [lambda x: x, lambda x: x],
                self.tr("size"): [lambda x: x, lambda x: x],
                self.tr("parts slot"): [lambda x: x, lambda x: x],
                self.tr("movement"): [lambda x: x, lambda x: x],
                self.tr("movement type"): [lambda x: x, lambda x: x],
            }
        )
        if self._robot_view._widths:
            self._robot_view.set_column_width(self._robot_view._widths)

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
        if self._robot_view._widths:
            self._robot_view.set_column_width(self._robot_view._widths)
