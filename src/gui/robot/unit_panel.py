"""
机体侧边栏面板 - 分组卡片布局与数据编辑

提供机体数据的编辑和搜索功能。继承 ProxyFrame，
自动传播 resetUI / translateUI 至子控件。

各类卡片拆分为独立子类，UnitPanel 只负责编排和接口转发。

Classes:
    _BaseCard:      面板卡片基类
    TransformCard:  变形·合体卡片
    TerrainCard:    地形适性卡片
    UnitPanel:      机体侧边栏面板
"""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QSizePolicy, QVBoxLayout
from qfluentwidgets import BodyLabel, HeaderCardWidget, setFont

from gui.custom.enums import EnumData
from gui.custom.models import BaseTableModel
from gui.custom.proxy_frame import ProxyFrame
from gui.custom.widgets import BitComboBox, MappingCompSpin


class _BaseCard(HeaderCardWidget):
    """面板卡片基类 - 统一卡片的样式和接口"""

    panelDataChanged = Signal(str)  # 字段名，供 UnitPanel 转发

    def __init__(self, title: str, parent=None):
        """初始化卡片

        Args:
            title: 卡片标题（tr 键）
            parent: 父 QWidget
        """
        super().__init__(parent)
        self.setTitle(self.tr(title))
        self.setBorderRadius(8)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        self.viewLayout.setContentsMargins(12, 8, 12, 8)

    # ========== UnitPanel 转发接口 ==========

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


class TransformCard(_BaseCard):
    """变形·合体卡片 - （待实现）"""

    def __init__(self, parent=None):
        """初始化变形·合体卡片"""
        super().__init__("Transform & Combine", parent)

    def set_model(self, model: BaseTableModel) -> None:
        """注入数据模型（待实现）"""
        pass

    def set_row(self, row: int) -> None:
        """切换行数据（待实现）"""
        pass

    def translateUI(self) -> None:
        """刷新卡片标题"""
        self.setTitle(self.tr("Transform & Combine"))

    def resetUI(self) -> None:
        """刷新卡片字体"""
        setFont(self)
        setFont(self.headerLabel, 15, QFont.DemiBold)


class TerrainCard(_BaseCard):
    """地形适性卡片 - 移动类型 + 四项地形适性"""

    def __init__(self, parent=None):
        """初始化地形适性卡片"""
        super().__init__("Terrain", parent)

        # ========== 控件 ==========

        # Bit 位多选下拉框 — 移动类型
        self._move_combo = BitComboBox("type", values=[], sep="")
        self._move_combo.setMinimumWidth(100)
        self._move_combo.dataChanged.connect(self.panelDataChanged)

        # 地形适性微调框 × 4
        _adapt_mapping = EnumData().ROBOT["ADAPT"]

        self._air_label = BodyLabel(self.tr("Air"), self)
        self._air_spin = MappingCompSpin("air", mapping=_adapt_mapping, parent=self)
        self._air_spin.setFixedWidth(70)
        self._air_spin.dataChanged.connect(self.panelDataChanged)

        self._grd_label = BodyLabel(self.tr("Ground"), self)
        self._grd_spin = MappingCompSpin("grd", mapping=_adapt_mapping, parent=self)
        self._grd_spin.setFixedWidth(70)
        self._grd_spin.dataChanged.connect(self.panelDataChanged)

        self._wtr_label = BodyLabel(self.tr("Water"), self)
        self._wtr_spin = MappingCompSpin("wtr", mapping=_adapt_mapping, parent=self)
        self._wtr_spin.setFixedWidth(70)
        self._wtr_spin.dataChanged.connect(self.panelDataChanged)

        self._spc_label = BodyLabel(self.tr("Space"), self)
        self._spc_spin = MappingCompSpin("spc", mapping=_adapt_mapping, parent=self)
        self._spc_spin.setFixedWidth(70)
        self._spc_spin.dataChanged.connect(self.panelDataChanged)

        # ========== 网格布局 ==========

        _grid = QGridLayout()
        _grid.setSpacing(4)
        _grid.setHorizontalSpacing(8)
        _grid.addWidget(self._move_combo, 0, 0, 1, 2)
        _grid.addWidget(self._air_label, 1, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        _grid.addWidget(self._air_spin, 1, 1)
        _grid.addWidget(self._grd_label, 2, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        _grid.addWidget(self._grd_spin, 2, 1)
        _grid.addWidget(self._wtr_label, 3, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        _grid.addWidget(self._wtr_spin, 3, 1)
        _grid.addWidget(self._spc_label, 4, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
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
        self._grd_label.setText(self.tr("Ground"))
        self._grd_spin.set_mapping(_enum.ROBOT["ADAPT"])
        self._wtr_label.setText(self.tr("Water"))
        self._wtr_spin.set_mapping(_enum.ROBOT["ADAPT"])
        self._spc_label.setText(self.tr("Space"))
        self._spc_spin.set_mapping(_enum.ROBOT["ADAPT"])

    def resetUI(self) -> None:
        """刷新所有控件字体"""
        self._move_combo.resetUI()
        self._air_spin.resetUI()
        self._grd_spin.resetUI()
        self._wtr_spin.resetUI()
        self._spc_spin.resetUI()
        setFont(self)
        setFont(self.headerLabel, 15, QFont.DemiBold)
        setFont(self._air_label)
        setFont(self._grd_label)
        setFont(self._wtr_label)
        setFont(self._spc_label)


class UnitPanel(ProxyFrame):
    """机体侧边栏面板 - 分组卡片编辑区，负责布局与接口转发"""

    panelDataChanged = Signal(str)  # 字段名，供 RobotFrame 刷新 model

    def __init__(self, parent=None):
        """初始化机体侧边栏面板

        Args:
            parent: 父 QWidget
        """
        super().__init__(parent)

        # ========== 面板尺寸（默认隐藏） ==========

        self._panel_open: bool = False
        self.setMinimumWidth(0)
        self.setMaximumWidth(0)

        # ========== 展开/收起动画（由外部传入目标宽度） ==========

        self._width_anim = QPropertyAnimation(self, b"maximumWidth")
        self._width_anim.setDuration(250)
        self._width_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        # ========== 创建卡片 ==========

        self._transform_card = TransformCard(self)
        self._transform_card.panelDataChanged.connect(self.panelDataChanged)

        self._terrain_card = TerrainCard(self)
        self._terrain_card.panelDataChanged.connect(self.panelDataChanged)

        # ========== 布局 ==========

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        # 卡片水平包裹，避免卡片被撑宽到面板宽度
        card_hbox = QHBoxLayout()
        card_hbox.addWidget(self._transform_card)
        card_hbox.addWidget(self._terrain_card)
        card_hbox.addStretch()
        layout.addLayout(card_hbox)
        layout.addStretch()

        self.setLayout(layout)

        # 触发初始翻译
        self.translateUI()

    # ========== 翻译 ==========

    def translateUI(self):
        """刷新卡片标题、标签文本及下拉选项"""
        self._transform_card.translateUI()
        self._terrain_card.translateUI()

    # ========== 主题刷新 ==========

    def resetUI(self):
        """刷新主框字体"""
        self._transform_card.resetUI()
        self._terrain_card.resetUI()
        super().resetUI()

    # ========== 行数据 ==========

    def set_model(self, model: BaseTableModel) -> None:
        """注入数据模型，转发至各卡片"""
        self._transform_card.set_model(model)
        self._terrain_card.set_model(model)

    def set_row(self, row: int) -> None:
        """切换行并刷新所有子编辑器

        Args:
            row: 源模型行号
        """
        self._transform_card.set_row(row)
        self._terrain_card.set_row(row)

    # ========== 面板展开/收起 ==========

    def open_panel(self, width: int) -> None:
        """展开面板至指定宽度

        Args:
            width: 展开目标宽度（由列折叠释放的空间决定）
        """
        if self._panel_open:
            return
        self._panel_open = True
        self._width_anim.stop()
        self._width_anim.setStartValue(self.width())
        self._width_anim.setEndValue(width)
        self._width_anim.start()

    def close_panel(self) -> None:
        """收起面板至 0"""
        if not self._panel_open:
            return
        self._panel_open = False
        self._width_anim.stop()
        self._width_anim.setStartValue(self.width())
        self._width_anim.setEndValue(0)
        self._width_anim.start()
