"""
武器表格视图 - 3 列武器数据编辑

提供武器名称、分类、攻击力等核心列的原地编辑。
射程/命中/会心移至右侧面板编辑。
继承 FixedTableView，自动配置字段委托和列宽。

Classes:
    WeaponView: 武器表格视图
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHeaderView, QSizePolicy

from gui.custom.widgets.card_header import CardHeader

from gui.custom.delegates import MappingSpinDelegate, NumberSpinDelegate, SingleLineDelegate
from gui.custom.enums import EnumData
from gui.custom.fonts import JP_FONT

from gui.custom.views import FixedTableView


class WeaponView(FixedTableView):
    """武器表格视图 - 武器核心数据编辑表格

    第 0 列（武器名）使用日语字体。
    列折叠后仅显示第 0 列，折叠/展开信号由 FixedTableView 自带 foldToggled 发出。
    """

    def __init__(self, parent=None):
        """初始化武器表格视图，配置 3 列委托"""
        super().__init__(parent)

        # ========== 委托编辑器 ==========

        self._name_delegate = SingleLineDelegate(font=JP_FONT, parent=self)
        self.setItemDelegateForColumn(0, self._name_delegate)

        _enum = EnumData()
        self._class_delegate = MappingSpinDelegate(mapping=_enum.WEAPON["CLASS"], wrapping=True, parent=self)
        self.setItemDelegateForColumn(1, self._class_delegate)

        self._damage_delegate = NumberSpinDelegate(show_buttons=False, parent=self)
        self.setItemDelegateForColumn(2, self._damage_delegate)

        # ========== 禁止排序 ==========

        # FixedTableView 使用自定义 _SortHeader，有独立的排序信号链，
        # 断掉所有排序相关信号让表头完全无响应
        self.setSortingEnabled(False)
        for signal_name in ("sectionClicked", "sortChanged"):
            try:
                getattr(self.horizontalHeader(), signal_name).disconnect()
            except (TypeError, RuntimeError):
                pass

        # ========== 字体与对齐 ==========

        _model = self.source_model()
        _model.set_font({0: JP_FONT})
        _model.set_alignments(
            {
                1: Qt.AlignmentFlag.AlignCenter,
                2: Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            }
        )

        # ========== 默认列宽（暂存，数据加载后生效） ==========

        self._widths = [220, 140, 100]
        self.setShowGrid(False)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # 禁用折叠按钮（武器表格始终保持展开）
        self._corner_button.setVisible(False)

        # ========== 初始翻译 ==========

        self.translateUI()

    # ========== 数据装入后设定列宽 ==========

    def set_data(self, data: list[dict]) -> None:
        """装入数据后应用列宽设置"""
        super().set_data(data)
        if self._widths:
            self.set_column_width(self._widths)

    # ========== 翻译 ==========

    def translateUI(self):
        """刷新列标题与格式化函数"""
        _enum = EnumData()
        self._class_delegate = MappingSpinDelegate(mapping=_enum.WEAPON["CLASS"], wrapping=True, parent=self)
        self.setItemDelegateForColumn(1, self._class_delegate)

        self.set_title(
            {
                self.tr("Weapon name"): [self._name_delegate.format_display, self._name_delegate.parse_display],
                self.tr("Class"): [self._class_delegate.format_display, self._class_delegate.parse_display],
                self.tr("Damage"): [self._damage_delegate.format_display, self._damage_delegate.parse_display],
            }
        )


class WeaponListCard(CardHeader):
    """武器列表卡片 - 只显示标题，内容由外层填入"""

    def __init__(self, parent=None):
        """初始化武器列表卡片"""
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setTitle(self.tr("Weapon list"))
        self.viewLayout.setContentsMargins(0, 0, 0, 0)

    def translateUI(self):
        """刷新标题翻译"""
        self.setTitle(self.tr("Weapon list"))

    def resetUI(self):
        """空实现，字体由子控件自行管理"""
        pass
