"""
CardHeader 面板卡片基类

统一 HeaderCardWidget 的样式和数据接口，供各编辑器面板的卡片子类继承。
卡片持有 model 引用和当前行号，负责读/写 model 数据并编排子控件。

Classes:
    CardHeader: 面板卡片基类
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QSizePolicy
from qfluentwidgets import HeaderCardWidget

from gui.widget.table import BaseTableModel


class CardHeader(HeaderCardWidget):
    """面板卡片基类 - 统一卡片的样式、数据读写接口

    子类在 __init__ 中创建纯信号槽控件并连接 valueChanged → _write(field, v)。
    子类重写 set_row 读取各字段值并通过 set_value 分发给控件。

    Signals:
        panelDataChanged: 字段名，供外层转发给 Frame 刷新表格
    """

    panelDataChanged = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setBorderRadius(8)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.viewLayout.setContentsMargins(12, 8, 12, 8)

        self._model: BaseTableModel | None = None
        self._row: int = -1

    def mousePressEvent(self, e):
        """点击卡片空白区域时交出焦点"""
        focused = self.focusWidget()
        if focused:
            focused.clearFocus()
        super().mousePressEvent(e)

    # ========== 数据接口 ==========

    def set_model(self, model: BaseTableModel) -> None:
        """注入数据模型，子类可转发给内嵌卡片"""
        self._model = model

    def set_row(self, row: int) -> None:
        """切换行，子类必须重写以刷新控件"""
        self._row = row

    def _read(self, field: str):
        """从当前行读取字段值

        Args:
            field: 字段名

        Returns:
            字段值，行或模型无效时返回 None
        """
        if self._model is not None and self._row >= 0:
            return self._model.get_row_data(self._row).get(field)
        return None

    def _write(self, field: str, value) -> None:
        """将值写回当前行的指定字段并发射 panelDataChanged

        Args:
            field: 字段名
            value: 新值
        """
        if self._model is not None and self._row >= 0:
            self._model.get_row_data(self._row)[field] = value
        self.panelDataChanged.emit(field)

    # ========== 子类扩展点 ==========

    def translateUI(self) -> None:
        """子类重写 - 刷新翻译"""

    def resetUI(self) -> None:
        """子类重写 - 刷新字体"""
