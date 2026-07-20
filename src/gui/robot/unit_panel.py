"""
机体侧边栏面板 - 分组卡片布局与数据编辑

提供机体数据的编辑和搜索功能。继承 ProxyFrame，
自动传播 resetUI / translateUI 至子控件。

各类卡片拆分为独立子类，UnitPanel 只负责编排和接口转发。

Classes:
    TransformCard:  变形·合体卡片
    TerrainCard:    地形适性卡片
    AbilitiesCard:  能力列表卡片
    UnitPanel:      机体侧边栏面板
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QSizePolicy, QVBoxLayout
from qfluentwidgets import BodyLabel, setFont

from gui.custom.fonts import JP_FONT, JP_QFONT
from gui.custom.enums import EnumData
from gui.custom.models import BaseTableModel
from gui.custom.widgets.proxy_frame import ProxyFrame
from gui.custom.widgets import BitCheckList, BitComboBox, MappingComboBox, MappingCompSpin, NumberCompSpin
from gui.custom.widgets.card_header import CardHeader
from gui.custom.widgets.special import RobotComboBox


class TransformCard(CardHeader):
    """变形·合体卡片 - 变形组与变形序号"""

    def __init__(self, parent=None):
        """初始化变形·合体卡片"""
        super().__init__(parent)
        self.setTitle(self.tr("Transform & Combine"))

        # ========== 控件 ==========

        _align = Qt.AlignmentFlag.AlignLeft
        self._lbl_tgrp = BodyLabel(self.tr("Tran Grp"), self)
        self._lbl_tgrp.setAlignment(_align)
        self._tgrp_spin = NumberCompSpin("tgrp", value_range=(0, 99), parent=self)
        self._tgrp_spin.setMinimumWidth(70)
        self._tgrp_spin.dataChanged.connect(self.panelDataChanged)
        self._lbl_tsn = BodyLabel(self.tr("Tran Seq"), self)
        self._lbl_tsn.setAlignment(_align)
        self._tsn_spin = NumberCompSpin("tsn", value_range=(0, 2), parent=self)
        self._tsn_spin.setMinimumWidth(65)
        self._tsn_spin.dataChanged.connect(self.panelDataChanged)

        self._lbl_cgrp = BodyLabel(self.tr("Comb Grp"), self)
        self._lbl_cgrp.setAlignment(_align)
        self._cgrp_spin = NumberCompSpin("cgrp", value_range=(0, 99), parent=self)
        self._cgrp_spin.setMinimumWidth(70)
        self._cgrp_spin.dataChanged.connect(self.panelDataChanged)
        self._lbl_csn = BodyLabel(self.tr("Comb Seq"), self)
        self._lbl_csn.setAlignment(_align)
        self._csn_spin = NumberCompSpin("csn", value_range=(0, 2), parent=self)
        self._csn_spin.setMinimumWidth(65)
        self._csn_spin.dataChanged.connect(self.panelDataChanged)

        self._lbl_cnt = BodyLabel(self.tr("Comb Cnt"), self)
        self._lbl_cnt.setAlignment(_align)
        self._cnt_spin = NumberCompSpin("count", value_range=(0, 5), parent=self)
        self._cnt_spin.setMinimumWidth(65)
        self._cnt_spin.dataChanged.connect(self.panelDataChanged)

        self._lbl_core = BodyLabel(self.tr("Core Unit"), self)
        self._lbl_core.setAlignment(_align)
        self._core_combo = RobotComboBox("core", parent=self, supplements={0xFFFF: "一一"})
        self._core_combo.setMinimumWidth(250)
        self._core_combo.dataChanged.connect(self.panelDataChanged)

        self._lbl_option = BodyLabel(self.tr("Unit Opt"), self)
        self._lbl_option.setAlignment(_align)
        _option_mapping = EnumData().ROBOT["OPTION"]
        self._option_combo = MappingComboBox("option", mapping=_option_mapping, parent=self)
        self._option_combo.apply_font(JP_FONT)
        self._option_combo.set_dropdown_font(JP_QFONT)
        self._option_combo.dataChanged.connect(self.panelDataChanged)

        # ========== 网格布局 ==========

        _grid = QGridLayout()
        _grid.setSpacing(4)
        _grid.setHorizontalSpacing(8)
        _grid.addWidget(self._lbl_tgrp, 0, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        _grid.addWidget(self._tgrp_spin, 0, 1)
        _grid.addWidget(self._lbl_tsn, 0, 2, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        _grid.addWidget(self._tsn_spin, 0, 3)
        _grid.addWidget(self._lbl_cgrp, 1, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        _grid.addWidget(self._cgrp_spin, 1, 1)
        _grid.addWidget(self._lbl_csn, 1, 2, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        _grid.addWidget(self._csn_spin, 1, 3)
        _grid.addWidget(self._lbl_core, 2, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        _grid.addWidget(self._lbl_cnt, 2, 2, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        _grid.addWidget(self._cnt_spin, 2, 3)
        _grid.addWidget(self._core_combo, 3, 0, 1, 4)
        _grid.addWidget(self._lbl_option, 4, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        _grid.addWidget(self._option_combo, 4, 1, 1, 3)
        self.viewLayout.addLayout(_grid)
        self.viewLayout.addStretch()

    # ========== UnitPanel 转发接口 ==========

    def set_model(self, model: BaseTableModel) -> None:
        """注入数据模型，转发至各子编辑器"""
        self._tgrp_spin.set_model(model)
        self._tsn_spin.set_model(model)
        self._cgrp_spin.set_model(model)
        self._csn_spin.set_model(model)
        self._cnt_spin.set_model(model)
        self._core_combo.set_model(model)
        self._option_combo.set_model(model)

    def set_row(self, row: int) -> None:
        """切换行并刷新所有子编辑器"""
        self._tgrp_spin.set_row(row)
        self._tsn_spin.set_row(row)
        self._cgrp_spin.set_row(row)
        self._csn_spin.set_row(row)
        self._cnt_spin.set_row(row)
        self._core_combo.set_row(row)
        self._option_combo.set_row(row)

    def translateUI(self) -> None:
        """刷新卡片标题与标签"""
        self.setTitle(self.tr("Transform & Combine"))
        self._lbl_tgrp.setText(self.tr("Tran Grp"))
        self._lbl_tsn.setText(self.tr("Tran Seq"))
        self._lbl_cgrp.setText(self.tr("Comb Grp"))
        self._lbl_csn.setText(self.tr("Comb Seq"))
        self._lbl_cnt.setText(self.tr("Comb Cnt"))
        self._lbl_core.setText(self.tr("Core Unit"))
        self._lbl_option.setText(self.tr("Unit Opt"))
        self._option_combo.set_mapping(EnumData().ROBOT["OPTION"])

    def resetUI(self) -> None:
        """刷新所有控件字体"""
        self._tgrp_spin.resetUI()
        self._tsn_spin.resetUI()
        self._cgrp_spin.resetUI()
        self._csn_spin.resetUI()
        self._cnt_spin.resetUI()
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
        setFont(self._lbl_tgrp)
        setFont(self._lbl_tsn)
        setFont(self._lbl_cgrp)
        setFont(self._lbl_csn)
        setFont(self._lbl_cnt)
        setFont(self._lbl_core)
        self._option_combo.resetUI()
        setFont(self._lbl_option)


class TerrainCard(CardHeader):
    """地形适性卡片 - 移动类型 + 四项地形适性"""

    def __init__(self, parent=None):
        """初始化地形适性卡片"""
        super().__init__(parent)
        self.setTitle(self.tr("Terrain"))

        # ========== 控件 ==========

        _align = Qt.AlignmentFlag.AlignCenter

        # Bit 位多选下拉框 — 移动类型
        self._move_combo = BitComboBox("type", values=[], sep="")
        self._move_combo.setMinimumWidth(110)
        self._move_combo.dataChanged.connect(self.panelDataChanged)

        # 地形适性微调框 × 4
        _adapt_mapping = EnumData().ROBOT["ADAPT"]

        self._air_label = BodyLabel(self.tr("Air"), self)
        self._air_label.setAlignment(_align)
        self._air_spin = MappingCompSpin("air", mapping=_adapt_mapping, parent=self)
        self._air_spin.setMinimumWidth(65)
        self._air_spin.dataChanged.connect(self.panelDataChanged)

        self._grd_label = BodyLabel(self.tr("Lnd"), self)
        self._grd_label.setAlignment(_align)
        self._grd_spin = MappingCompSpin("grd", mapping=_adapt_mapping, parent=self)
        self._grd_spin.setMinimumWidth(65)
        self._grd_spin.dataChanged.connect(self.panelDataChanged)

        self._wtr_label = BodyLabel(self.tr("Sea"), self)
        self._wtr_label.setAlignment(_align)
        self._wtr_spin = MappingCompSpin("wtr", mapping=_adapt_mapping, parent=self)
        self._wtr_spin.setMinimumWidth(65)
        self._wtr_spin.dataChanged.connect(self.panelDataChanged)

        self._spc_label = BodyLabel(self.tr("Spc"), self)
        self._spc_label.setAlignment(_align)
        self._spc_spin = MappingCompSpin("spc", mapping=_adapt_mapping, parent=self)
        self._spc_spin.setMinimumWidth(65)
        self._spc_spin.dataChanged.connect(self.panelDataChanged)

        # ========== 网格布局 ==========

        _grid = QGridLayout()
        _grid.setSpacing(4)
        _grid.setHorizontalSpacing(8)
        _grid.addWidget(self._move_combo, 0, 0, 1, 2)
        _grid.addWidget(self._air_label, 1, 0, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._air_spin, 1, 1)
        _grid.addWidget(self._grd_label, 2, 0, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._grd_spin, 2, 1)
        _grid.addWidget(self._wtr_label, 3, 0, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._wtr_spin, 3, 1)
        _grid.addWidget(self._spc_label, 4, 0, Qt.AlignmentFlag.AlignCenter)
        _grid.addWidget(self._spc_spin, 4, 1)
        self.viewLayout.addLayout(_grid)
        self.viewLayout.addStretch()

    # ========== UnitPanel 转发接口 ==========

    def set_model(self, model: BaseTableModel) -> None:
        """注入数据模型，转发至各子编辑器"""
        self._move_combo.set_model(model)
        self._air_spin.set_model(model)
        self._grd_spin.set_model(model)
        self._wtr_spin.set_model(model)
        self._spc_spin.set_model(model)

    def set_row(self, row: int) -> None:
        """切换行并刷新所有子编辑器"""
        self._move_combo.set_row(row)
        self._air_spin.set_row(row)
        self._grd_spin.set_row(row)
        self._wtr_spin.set_row(row)
        self._spc_spin.set_row(row)

    def translateUI(self) -> None:
        """刷新卡片标题、标签文本及下拉选项"""
        self.setTitle(self.tr("Terrain"))
        _enum = EnumData()
        self._move_combo.set_values(_enum.ROBOT["MOVETYPE"])
        self._air_label.setText(self.tr("Air"))
        self._air_spin.set_mapping(_enum.ROBOT["ADAPT"])
        self._grd_label.setText(self.tr("Lnd"))
        self._grd_spin.set_mapping(_enum.ROBOT["ADAPT"])
        self._wtr_label.setText(self.tr("Sea"))
        self._wtr_spin.set_mapping(_enum.ROBOT["ADAPT"])
        self._spc_label.setText(self.tr("Spc"))
        self._spc_spin.set_mapping(_enum.ROBOT["ADAPT"])

    def resetUI(self) -> None:
        """刷新所有控件字体"""
        self._move_combo.resetUI()
        self._air_spin.resetUI()
        self._grd_spin.resetUI()
        self._wtr_spin.resetUI()
        self._spc_spin.resetUI()
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
        setFont(self._air_label)
        setFont(self._grd_label)
        setFont(self._wtr_label)
        setFont(self._spc_label)


class AbilitiesCard(CardHeader):
    """能力列表卡片 - Bit 位多选能力列表"""

    def __init__(self, parent=None):
        """初始化能力列表卡片"""
        super().__init__(parent)
        self.setTitle(self.tr("Abilities"))

        # ========== Bit 位多选列表 ==========

        self._abil_list = BitCheckList("abi", parent=self)
        self._abil_list.dataChanged.connect(self.panelDataChanged)

        # 左右边距收窄以贴合滚动条
        self.viewLayout.setContentsMargins(3, 8, 3, 8)
        self.viewLayout.addWidget(self._abil_list)
        self.setMinimumWidth(200)

    # ========== UnitPanel 转发接口 ==========

    def set_model(self, model: BaseTableModel) -> None:
        """注入数据模型，转发至能力列表"""
        self._abil_list.set_model(model)

    def set_row(self, row: int) -> None:
        """切换行并刷新能力列表"""
        self._abil_list.set_row(row)

    def translateUI(self) -> None:
        """刷新卡片标题与能力列表选项"""
        self.setTitle(self.tr("Abilities"))
        self._abil_list.set_values(EnumData().ROBOT["ABILITIES"])

    def resetUI(self) -> None:
        """刷新所有控件字体"""
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
        self._abil_list.resetUI()


class _ExtraBitsCard(CardHeader):
    """占位卡片 - 待实现的额外 Bit 位多选列表（右侧纵向跨两行）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Extra Bits"))
        self.setMinimumWidth(160)

    def set_model(self, model: BaseTableModel) -> None:
        pass

    def set_row(self, row: int) -> None:
        pass

    def translateUI(self) -> None:
        self.setTitle(self.tr("Extra Bits"))

    def resetUI(self) -> None:
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)


class _BottomCard(CardHeader):
    """占位卡片 - 待实现的新卡片（底部横向跨两列）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("New Card"))
        self.setMinimumWidth(320)

    def set_model(self, model: BaseTableModel) -> None:
        pass

    def set_row(self, row: int) -> None:
        pass

    def translateUI(self) -> None:
        self.setTitle(self.tr("New Card"))

    def resetUI(self) -> None:
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)


class UnitPanel(ProxyFrame):
    """机体侧边栏面板 - 分组卡片编辑区，负责布局与接口转发"""

    panelDataChanged = Signal(str)  # 字段名，供 RobotFrame 刷新 model

    def __init__(self, parent=None):
        """初始化机体侧边栏面板

        Args:
            parent: 父 QWidget
        """
        super().__init__(parent)

        # ========== 面板尺寸与策略 ==========

        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)

        # ========== 创建卡片 ==========

        self._transform_card = TransformCard(self)
        self._transform_card.panelDataChanged.connect(self.panelDataChanged)

        self._terrain_card = TerrainCard(self)
        self._terrain_card.panelDataChanged.connect(self.panelDataChanged)

        self._abilities_card = AbilitiesCard(self)
        self._abilities_card.panelDataChanged.connect(self.panelDataChanged)

        self._extra_bits_card = _ExtraBitsCard(self)
        self._extra_bits_card.panelDataChanged.connect(self.panelDataChanged)

        self._bottom_card = _BottomCard(self)
        self._bottom_card.panelDataChanged.connect(self.panelDataChanged)

        # ========== 卡片网格布局 ==========
        #
        #   (0,0) TransformCard  │  (0,1) TerrainCard  │  (0,2) AbilitiesCard  │  (0,3) [待添加]
        #                         │                     │       row0-1          │       row0-1
        #   (1,0) [待添加] col0-1 │                     │                       │
        #                         │                     │                       │
        #
        # 四个纵向卡片列 + 底部横向跨列卡片

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        grid = QGridLayout()
        grid.setSpacing(8)
        grid.addWidget(self._transform_card, 0, 0)             # (0,0)
        grid.addWidget(self._terrain_card, 0, 1)               # (0,1)
        grid.addWidget(self._abilities_card, 0, 2, 2, 1)       # (0,2) 跨 2 行
        grid.addWidget(self._extra_bits_card, 0, 3, 2, 1)      # (0,3) 跨 2 行
        grid.addWidget(self._bottom_card, 1, 0, 1, 2)           # (1,0) 跨 2 列
        layout.addLayout(grid)
        layout.addStretch()

        self.setLayout(layout)

        # 触发初始翻译
        self.translateUI()

    # ========== 翻译 ==========

    def translateUI(self):
        """刷新卡片标题、标签文本及下拉选项"""
        self._transform_card.translateUI()
        self._terrain_card.translateUI()
        self._abilities_card.translateUI()
        self._extra_bits_card.translateUI()
        self._bottom_card.translateUI()

    # ========== 主题刷新 ==========

    def resetUI(self):
        """刷新主框字体"""
        self._transform_card.resetUI()
        self._terrain_card.resetUI()
        self._abilities_card.resetUI()
        self._extra_bits_card.resetUI()
        self._bottom_card.resetUI()
        super().resetUI()

    # ========== 行数据 ==========

    def set_model(self, model: BaseTableModel) -> None:
        """注入数据模型，转发至各卡片"""
        self._transform_card.set_model(model)
        self._terrain_card.set_model(model)
        self._abilities_card.set_model(model)
        self._extra_bits_card.set_model(model)
        self._bottom_card.set_model(model)

    def set_row(self, row: int) -> None:
        """切换行并刷新所有子编辑器

        Args:
            row: 源模型行号
        """
        self._transform_card.set_row(row)
        self._terrain_card.set_row(row)
        self._abilities_card.set_row(row)
        self._extra_bits_card.set_row(row)
        self._bottom_card.set_row(row)

    # ========== 面板展开/收起 ==========

    def set_fold_mode(self, folded: bool, target_width: int = 0) -> None:
        """切换面板折叠状态

        折叠时用 setFixedWidth 固定面板宽度，展开时设为 0（由外层 hide() 配合）。

        Args:
            folded:   True=面板展开显示，False=面板收起
            target_width: 折叠状态下面板的目标宽度（仅 folded=True 有效）
        """
        if folded:
            self.setFixedWidth(target_width)
        else:
            self.setFixedWidth(0)
