"""
驾驶员系列卡片

提供换乘系列 Bit 位多选列表编辑。
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSizePolicy
from qfluentwidgets import setFont

from gui.custom import EnumData
from gui.widget import CardHeader, CommonBitList


class SeriesCard(CardHeader):
    """系列卡片 - Bit 位多选换乘系列列表"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Series"))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self._series_list = CommonBitList(parent=self)
        self._series_list.valueChanged.connect(lambda v: self._write("series", v))

        self.viewLayout.setContentsMargins(3, 8, 3, 8)
        self.viewLayout.addWidget(self._series_list)

    def set_row(self, row: int) -> None:
        super().set_row(row)
        self._series_list.set_value(self._read("series"))

    def translateUI(self) -> None:
        self.setTitle(self.tr("Series"))
        self._series_list.set_values(EnumData().PILOT["SERIES"])

    def resetUI(self) -> None:
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
        self._series_list.resetUI()
