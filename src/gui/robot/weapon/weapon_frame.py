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
    WeaponAdaptCard: 地形适应卡片（占位）
    WeaponPanel:    右侧面板容器
    WeaponFrame:    武器编辑框架
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout
from qfluentwidgets import setFont

from gui.custom.models import BaseTableModel
from gui.custom.widgets.card_header import CardHeader
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
    """地形适应卡片 - 四项地形适性

    待填充字段：air, grd, wtr, spc
    """

    def __init__(self, parent=None):
        """初始化地形适应卡片"""
        super().__init__(parent)
        self.setTitle(self.tr("Terrain"))

    # ========== UnitPanel 转发接口 ==========

    def set_model(self, model: BaseTableModel) -> None:
        """注入数据模型"""
        pass

    def set_row(self, row: int) -> None:
        """切换行数据"""
        pass

    def translateUI(self) -> None:
        """刷新卡片标题"""
        self.setTitle(self.tr("Terrain"))

    def resetUI(self) -> None:
        """刷新字体"""
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)


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
