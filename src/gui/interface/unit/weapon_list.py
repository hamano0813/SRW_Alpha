"""
武器列表卡片

自含 FixedTableView 的卡片，提供武器名称、分类、攻击力的原地编辑。
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHeaderView, QSizePolicy

from gui.custom import EnumData, JP_FONT
from gui.widget import (
    CardHeader,
    FixedTableView,
    MappingSpinDelegate,
    NumberSpinDelegate,
    SingleLineDelegate,
)


class WeaponListCard(CardHeader):
    """武器列表卡片 - 自含武器编辑表格"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setTitle(self.tr("Weapon list"))
        self.viewLayout.setContentsMargins(0, 0, 0, 0)

        # ========== 内部表格 ==========

        self._view = WeaponView(self)
        self.viewLayout.addWidget(self._view)

    # ========== 代理到内部视图 ==========

    @property
    def table(self) -> "WeaponView":
        return self._view

    def set_field(self, fields) -> None:
        self._view.set_field(fields)

    def set_data(self, data: list[dict]) -> None:
        self._view.set_data(data)

    def source_model(self):
        return self._view.source_model()

    def select_source_row(self, row: int) -> None:
        self._view.select_source_row(row)

    def translateUI(self):
        self.setTitle(self.tr("Weapon list"))
        self._view.translateUI()

    def resetUI(self):
        self._view.resetUI()


class WeaponView(FixedTableView):
    """武器表格视图 - 3 列武器核心数据编辑

    第 0 列（武器名）使用日语字体。
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._name_delegate = SingleLineDelegate(font=JP_FONT, parent=self)
        self.setItemDelegateForColumn(0, self._name_delegate)

        _enum = EnumData()
        self._class_delegate = MappingSpinDelegate(mapping=_enum.WEAPON["CLASS"], wrapping=True, parent=self)
        self.setItemDelegateForColumn(1, self._class_delegate)

        self._damage_delegate = NumberSpinDelegate(show_buttons=False, parent=self)
        self.setItemDelegateForColumn(2, self._damage_delegate)

        self.setSortingEnabled(False)
        for signal_name in ("sectionClicked", "sortChanged"):
            try:
                getattr(self.horizontalHeader(), signal_name).disconnect()
            except (TypeError, RuntimeError):
                pass

        _model = self.source_model()
        _model.set_font({0: JP_FONT})
        _model.set_alignments({
            1: Qt.AlignmentFlag.AlignCenter,
            2: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
        })

        self._widths = [220, 140, 100]
        self.setShowGrid(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self._corner_button.setVisible(False)

        self.translateUI()

    def set_data(self, data: list[dict]) -> None:
        super().set_data(data)
        if self._widths:
            self.set_column_width(self._widths)

    def translateUI(self):
        _enum = EnumData()
        self._class_delegate = MappingSpinDelegate(mapping=_enum.WEAPON["CLASS"], wrapping=True, parent=self)
        self.setItemDelegateForColumn(1, self._class_delegate)
        self.set_title({
            self.tr("Weapon name"): [self._name_delegate.format_display, self._name_delegate.parse_display],
            self.tr("Class"): [self._class_delegate.format_display, self._class_delegate.parse_display],
            self.tr("Damage"): [self._damage_delegate.format_display, self._damage_delegate.parse_display],
        })
