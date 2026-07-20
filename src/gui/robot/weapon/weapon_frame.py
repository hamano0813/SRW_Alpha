"""
武器编辑子框架 - 武器表格 + 右侧面板

包含 WeaponView（武器表格）和 3 张编辑卡片。
采用类似 RobotFrame 的折叠布局：
- 表格展开时占满整个宽度，面板隐藏
- 表格折叠（仅第 0 列）时面板出现在右侧

WeaponFrame 自身不管理外层高度，由父级（RobotFrame）通过 setGeometry 定位。

Classes:
    WeaponAttrCard: 武器属性卡片（占位）
    WeaponMapCard:  地图武器卡片（占位）
    WeaponAdaptCard: 地形适应卡片（空陆海宇）
    WeaponPanel:    右侧面板容器
    WeaponFrame:    武器编辑框架
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QVBoxLayout
from qfluentwidgets import BodyLabel, setFont

from gui.custom.enums import EnumData
from gui.custom.models import BaseTableModel
from gui.custom.widgets.card_header import CardHeader
from gui.custom.widgets.panel.mapping_compspin import MappingCompSpin
from gui.custom.widgets.proxy_frame import ProxyFrame

from .weapon_view import WeaponView


# =============================================================================
# 卡片占位 — 各卡片内容后续逐步填充
# =============================================================================


class WeaponAttrCard(CardHeader):
    """武器属性卡片 - 武器分类/改造/气力/EN/NT等级等

    待填充字段：custom, bonus, morale, newtype, aura, encost, attr
    """

    def __init__(self, parent=None):
        """初始化武器属性卡片"""
        super().__init__(parent)
        self.setTitle(self.tr("Attributes"))

    # ========== UnitPanel 转发接口 ==========

    def set_model(self, model: BaseTableModel) -> None:
        """注入数据模型"""
        pass

    def set_row(self, row: int) -> None:
        """切换行数据"""
        pass

    def translateUI(self) -> None:
        """刷新卡片标题"""
        self.setTitle(self.tr("Attributes"))

    def resetUI(self) -> None:
        """刷新字体"""
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)


class WeaponMapCard(CardHeader):
    """地图武器卡片 - 地图武器参数

    待填充字段：mcls, radius, mshow, mrng
    """

    def __init__(self, parent=None):
        """初始化地图武器卡片"""
        super().__init__(parent)
        self.setTitle(self.tr("Map Weapon"))

    # ========== UnitPanel 转发接口 ==========

    def set_model(self, model: BaseTableModel) -> None:
        """注入数据模型"""
        pass

    def set_row(self, row: int) -> None:
        """切换行数据"""
        pass

    def translateUI(self) -> None:
        """刷新卡片标题"""
        self.setTitle(self.tr("Map Weapon"))

    def resetUI(self) -> None:
        """刷新字体"""
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)


class WeaponAdaptCard(CardHeader):
    """地形适应卡片 - 四项地形适性一字横排"""

    def __init__(self, parent=None):
        """初始化地形适应卡片"""
        super().__init__(parent)
        self.setTitle(self.tr("Terrain"))

        # ========== 控件 ==========

        _adapt_mapping = EnumData().WEAPON["ADAPT"]
        _align = Qt.AlignmentFlag.AlignCenter

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

        # ========== 一字横排布局 ==========

        _hbox = QHBoxLayout()
        _hbox.setSpacing(4)
        for label, spin in [
            (self._air_label, self._air_spin),
            (self._grd_label, self._grd_spin),
            (self._wtr_label, self._wtr_spin),
            (self._spc_label, self._spc_spin),
        ]:
            _hbox.addWidget(label, 0, Qt.AlignmentFlag.AlignVCenter)
            _hbox.addWidget(spin, 0, Qt.AlignmentFlag.AlignVCenter)
        _hbox.addStretch()
        self.viewLayout.addLayout(_hbox)
        self.viewLayout.addStretch()

    # ========== UnitPanel 转发接口 ==========

    def set_model(self, model: BaseTableModel) -> None:
        """注入数据模型，转发至各子编辑器"""
        self._air_spin.set_model(model)
        self._grd_spin.set_model(model)
        self._wtr_spin.set_model(model)
        self._spc_spin.set_model(model)

    def set_row(self, row: int) -> None:
        """切换行并刷新所有控件"""
        self._air_spin.set_row(row)
        self._grd_spin.set_row(row)
        self._wtr_spin.set_row(row)
        self._spc_spin.set_row(row)

    def translateUI(self) -> None:
        """刷新卡片标题和标签"""
        self.setTitle(self.tr("Terrain"))
        self._air_label.setText(self.tr("Air"))
        self._grd_label.setText(self.tr("Lnd"))
        self._wtr_label.setText(self.tr("Sea"))
        self._spc_label.setText(self.tr("Spc"))

    def resetUI(self) -> None:
        """刷新字体"""
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
        for label in [self._air_label, self._grd_label, self._wtr_label, self._spc_label]:
            setFont(label)


# =============================================================================
# 面板容器
# =============================================================================


class WeaponPanel(ProxyFrame):
    """武器右侧面板 - 3 张卡片竖直堆叠"""

    def __init__(self, parent=None):
        """初始化武器面板"""
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)

        # ========== 创建卡片 ==========

        self._attr_card = WeaponAttrCard(self)
        self._map_card = WeaponMapCard(self)
        self._adapt_card = WeaponAdaptCard(self)

        # ========== 竖直布局 ==========

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(self._attr_card)
        layout.addWidget(self._map_card)
        layout.addWidget(self._adapt_card)
        layout.addStretch()
        self.setLayout(layout)

    # ========== 行数据转发 ==========

    def set_model(self, model: BaseTableModel) -> None:
        """注入数据模型，转发至各卡片"""
        self._attr_card.set_model(model)
        self._map_card.set_model(model)
        self._adapt_card.set_model(model)

    def set_row(self, row: int) -> None:
        """切换行并刷新所有卡片"""
        self._attr_card.set_row(row)
        self._map_card.set_row(row)
        self._adapt_card.set_row(row)

    # ========== Theme / i18n ==========

    def translateUI(self) -> None:
        """刷新卡片标题"""
        self._attr_card.translateUI()
        self._map_card.translateUI()
        self._adapt_card.translateUI()

    def resetUI(self) -> None:
        """刷新字体"""
        self._attr_card.resetUI()
        self._map_card.resetUI()
        self._adapt_card.resetUI()
        super().resetUI()


# =============================================================================
# 框架（表格 + 面板）
# =============================================================================


class WeaponFrame(ProxyFrame):
    """武器编辑框架 - 武器表格 + 右侧面板（折叠后显示）

    内部布局：WeaponView（表格）在左，WeaponPanel（面板）在右。
    表格展开时面板隐藏、表格占满整宽；表格折叠后面板出现在右侧。
    """

    def __init__(self, parent=None):
        """初始化武器编辑框架"""
        super().__init__(parent)

        self._folded: bool = False

        # ========== 武器表格 ==========

        self._weapon_view = WeaponView(self)
        self._weapon_view.foldToggled.connect(self._on_fold_toggled)
        self._weapon_view.sClicked.connect(self._on_weapon_row_clicked)

        # ========== 右侧面板（默认隐藏） ==========

        self._weapon_panel = WeaponPanel(self)
        self._weapon_panel.setVisible(False)

    # ========== 布局 ==========

    def _update_layout(self):
        """根据折叠状态重算所有子控件位置"""
        w = self.width()
        h = self.height()
        if w <= 0 or h <= 0:
            return

        if self._folded:
            table_w = self._weapon_view.get_content_width(True)
        else:
            table_w = w

        self._weapon_view.setGeometry(0, 0, table_w, h)

        if self._folded:
            panel_w = self._weapon_panel.sizeHint().width()
            self._weapon_panel.setGeometry(table_w, 0, w - table_w, h)

    def resizeEvent(self, event):
        """尺寸变化时刷新布局"""
        super().resizeEvent(event)
        self._update_layout()

    # ========== 折叠联动 ==========

    def _on_fold_toggled(self, folded: bool, freed_width: int) -> None:
        """武器表格折叠时切换面板显示

        Args:
            folded:      True=列已折叠
            freed_width: 释放的像素宽度（此方案中不使用）
        """
        self._folded = folded
        self._weapon_panel.setVisible(folded)
        self._update_layout()

    # ========== 行选择 ==========

    def _on_weapon_row_clicked(self, source_row: int, model: BaseTableModel) -> None:
        """武器行单击时刷新面板卡片

        Args:
            source_row: 源模型行号
            model:      BaseTableModel 实例
        """
        self._weapon_panel.set_row(source_row)

    # ========== 数据接口 ==========

    def set_data(self, data: list[dict]) -> None:
        """装入武器列表数据并选中第一行

        Args:
            data: robots[N]["weapons"] 武器数据列表
        """
        self._weapon_view.set_data(data)

        # 将武器表格模型注入面板卡片
        model = self._weapon_view.source_model()
        self._weapon_panel.set_model(model)

        # 默认选中第一行
        if model.rowCount() > 0:
            self._weapon_view.select_source_row(0)
            self._on_weapon_row_clicked(0, model)

        self._update_layout()

    def set_field(self, fields) -> None:
        """设置字段映射，代理至武器表格模型

        Args:
            fields: FieldMapping 实例
        """
        self._weapon_view.set_field(fields)

    # ========== Theme / i18n ==========

    def translateUI(self) -> None:
        """刷新子控件翻译"""
        self._weapon_view.translateUI()
        self._weapon_panel.translateUI()
        # 翻译后列宽可能变化，重新布局
        self._update_layout()

    def resetUI(self) -> None:
        """刷新子控件字体"""
        self._weapon_view.resetUI()
        self._weapon_panel.resetUI()
        super().resetUI()
