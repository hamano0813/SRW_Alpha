"""
CardHeader 面板卡片基类

统一 HeaderCardWidget 的样式和接口，供各编辑器面板的卡片子类继承。

Classes:
    CardHeader: 面板卡片基类
"""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QSizePolicy
from qfluentwidgets import HeaderCardWidget

from gui.custom.models import BaseTableModel


class CardHeader(HeaderCardWidget):
    """面板卡片基类 - 统一卡片的样式和接口

    子类需在 __init__ 中用 self.setTitle(self.tr(...)) 设置标题，
    并重写 set_model / set_row / translateUI / resetUI。
    """

    panelDataChanged = Signal(str)  # 字段名，供外层面板转发

    def __init__(self, parent=None):
        """初始化卡片

        Args:
            parent: 父 QWidget
        """
        super().__init__(parent)
        self.setBorderRadius(8)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.viewLayout.setContentsMargins(12, 8, 12, 8)

    # ========== 外层面板转发接口 ==========

    def set_model(self, model: BaseTableModel) -> None:
        """子类重写 - 注入数据模型"""
        raise NotImplementedError

    def set_row(self, row: int) -> None:
        """子类重写 - 切换行数据"""
        raise NotImplementedError

    def translateUI(self) -> None:
        """子类重写 - 刷新翻译"""
        raise NotImplementedError

    def resetUI(self) -> None:
        """子类重写 - 刷新字体"""
        raise NotImplementedError
