"""
面板编辑器基类 — model[row][field] 模式

PanelEditor 持有 model 引用、行号和字段名，直接读写 model 内部数据。
dict 从不跨层传递，避免 PySide6 信号 QVariant 隐式复制。

与 TableEditor 的区别：
  TableEditor 操作单个值（set_value / get_value），
  PanelEditor 通过 model.get_row_data(row) 获取 dict 引用后按 field 存取。

放置于 widgets/panel/ 子包，供面板编辑器使用。

Classes:
    PanelEditor: 面板编辑器基类
"""

from typing import Any

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget

from gui.widget.table import BaseTableModel


class PanelEditor(QWidget):
    """面板编辑器基类 — 通过 model.get_row_data(row)[field] 读写

    set_model(model) 注入数据源，set_row(row) 切换行并刷新控件。
    编辑后 _emit_data_changed 原地回写 model 并发射字段名信号。

    Signals:
        dataChanged: 编辑确认后发射，携带字段名
    """

    dataChanged = Signal(str)

    def __init__(self, field: str = "", parent=None):
        """初始化面板编辑器

        Args:
            field: 数据字典中对应的键名
            parent: 父 QWidget
        """
        super().__init__(parent)
        self._field: str = field
        self._model: BaseTableModel | None = None
        self._row: int = -1
        self._value: Any = None

        # 所有面板编辑器禁用右键菜单
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

    # ========== 数据读写 ==========

    def set_model(self, model: BaseTableModel) -> None:
        """注入数据模型

        Args:
            model: BaseTableModel 子类实例
        """
        self._model = model

    def set_row(self, row: int) -> None:
        """切换当前行并刷新控件显示

        从 model.get_row_data(row)[field] 读取值写入 self._value。

        Args:
            row: 源模型行号
        """
        self._row = row
        if self._model is not None and row >= 0:
            self._value = self._model.get_row_data(row).get(self._field)
        else:
            self._value = None
        self.format_value()

    def _emit_data_changed(self) -> None:
        """写回 model 并发射 dataChanged 信号

        直接读写 model._data，不跨层传递 dict。
        子类在编辑确认后调用。
        """
        if self._model is not None and self._row >= 0:
            self._model.get_row_data(self._row)[self._field] = self._value
        self.dataChanged.emit(self._field)

    # ========== 子类扩展点 ==========

    def format_value(self) -> None:
        """刷新控件显示

        基类为空，子类重写。set_row 末尾自动调用。
        """
        pass

    # ========== 字体 ==========

    def apply_font(self, font: QFont | dict) -> None:
        """设置编辑器字体

        基类调用 setFont，子类如有内嵌控件需重写。

        Args:
            font: QFont 实例或字体属性字典
        """
        if isinstance(font, dict):
            qfont = QFont()
            family = font.get("family")
            size = font.get("size")
            weight = font.get("weight")
            italic = font.get("italic")
            if family:
                qfont.setFamily(family)
            if size:
                qfont.setPixelSize(size)
            if weight:
                qfont.setWeight(weight)
            if italic:
                qfont.setItalic(italic)
            font = qfont
        self.setFont(font)

    # ========== 主题刷新 ==========

    def resetUI(self):
        """从全局配置刷新字体，并传播至内嵌控件"""
        for child in self.children():
            if isinstance(child, QWidget) and hasattr(child, "resetUI"):
                child.resetUI()  # type: ignore
