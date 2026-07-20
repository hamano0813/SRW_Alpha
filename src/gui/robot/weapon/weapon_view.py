"""
武器表格视图 - 7 列武器数据编辑

提供武器名称、分类、射程、攻击力、命中、会心等核心列的原地编辑。
继承 FixedTableView，自动配置字段委托和列宽。

Classes:
    WeaponView: 武器表格视图
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView

from gui.custom.delegates import MappingSpinDelegate, NumberSpinDelegate, SingleLineDelegate
from gui.custom.enums import EnumData
from gui.custom.fonts import JP_FONT

from gui.custom.views import FixedTableView


class WeaponView(FixedTableView):
    """武器表格视图 - 武器核心数据编辑表格

    第 0 列（武器名）使用日语字体，数值列右对齐。
    列折叠后仅显示第 0 列，折叠/展开信号由 FixedTableView 自带 foldToggled 发出。
    """

    def __init__(self, parent=None):
        """初始化武器表格视图，配置 7 列委托"""
        super().__init__(parent)

        # ========== 委托编辑器 ==========

        self._name_delegate = SingleLineDelegate(font=JP_FONT, parent=self)
        self.setItemDelegateForColumn(0, self._name_delegate)

        # 非名称列先统一使用数值委托，后续逐步替换为 MappingSpinDelegate
        _enum = EnumData()
        self._class_delegate = MappingSpinDelegate(mapping=_enum.WEAPON["CLASS"], wrapping=True, parent=self)
        self.setItemDelegateForColumn(1, self._class_delegate)

        self._rngs_delegate = NumberSpinDelegate(value_range=(0, 3), show_buttons=True, parent=self)
        self.setItemDelegateForColumn(2, self._rngs_delegate)

        self._rngl_delegate = NumberSpinDelegate(value_range=(0, 15), show_buttons=True, parent=self)
        self.setItemDelegateForColumn(3, self._rngl_delegate)

        self._hit_delegate = NumberSpinDelegate(value_range=(-100, 100), show_sign=True, show_buttons=True, read_only=True, parent=self)
        self.setItemDelegateForColumn(4, self._hit_delegate)

        self._crt_delegate = NumberSpinDelegate(value_range=(-100, 100), show_sign=True, show_buttons=True, read_only=True, parent=self)
        self.setItemDelegateForColumn(5, self._crt_delegate)

        self._damage_delegate = NumberSpinDelegate(show_buttons=False, parent=self)
        self.setItemDelegateForColumn(6, self._damage_delegate)

        # ========== 字体与对齐 ==========

        _model = self.source_model()
        _model.set_font({0: JP_FONT})
        _model.set_alignments(
            {
                1: Qt.AlignmentFlag.AlignCenter,
                2: Qt.AlignmentFlag.AlignCenter,
                3: Qt.AlignmentFlag.AlignCenter,
                4: Qt.AlignmentFlag.AlignCenter,
                5: Qt.AlignmentFlag.AlignCenter,
                6: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            }
        )

        # ========== 默认列宽 ==========

        self.set_column_width([180, 130, 110, 110, 125, 125, 120])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)

        # ========== 初始翻译 ==========

        self.translateUI()

    # ========== 翻译 ==========

    def translateUI(self):
        """刷新列标题与格式化函数"""
        # 武器分类映射需要在语言切换后刷新
        _enum = EnumData()
        self._class_delegate = MappingSpinDelegate(mapping=_enum.WEAPON["CLASS"], wrapping=True, parent=self)
        self.setItemDelegateForColumn(1, self._class_delegate)

        self.set_title(
            {
                self.tr("Weapon name"): [self._name_delegate.format_display, self._name_delegate.parse_display],
                self.tr("Weapon class"): [self._class_delegate.format_display, self._class_delegate.parse_display],
                self.tr("Short range"): [self._rngs_delegate.format_display, self._rngs_delegate.parse_display],
                self.tr("Long range"): [self._rngl_delegate.format_display, self._rngl_delegate.parse_display],
                self.tr("Accuracy"): [self._hit_delegate.format_display, self._hit_delegate.parse_display],
                self.tr("Critical"): [self._crt_delegate.format_display, self._crt_delegate.parse_display],
                self.tr("Damage"): [self._damage_delegate.format_display, self._damage_delegate.parse_display],
            }
        )
        if self._widths:
            self.set_column_width(self._widths)
