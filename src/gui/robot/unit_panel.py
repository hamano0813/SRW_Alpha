"""
机体侧边栏面板 - 分组卡片布局与数据编辑

提供机体数据的编辑和搜索功能。继承 ProxyFrame，
自动传播 resetUI / translateUI 至子控件。

Classes:
    UnitPanel: 机体侧边栏面板
"""

from PySide6.QtCore import Qt, QEasingCurve, QPropertyAnimation
from PySide6.QtWidgets import QGridLayout, QVBoxLayout

from gui.custom.enums import EnumData
from gui.custom.proxy_frame import ProxyFrame
from gui.custom.widgets import BitComboBox, MappingCompSpin
from qfluentwidgets import BodyLabel, HeaderCardWidget


class UnitPanel(ProxyFrame):
    """机体侧边栏面板 - 分组卡片编辑区"""

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

        # ========== 地形适性卡片 ==========

        self._terrain_card = HeaderCardWidget(self)
        self._terrain_card.setTitle(self.tr("Terrain"))
        self._terrain_card.setBorderRadius(8)
        self._terrain_card.setMaximumWidth(220)
        self._terrain_card.viewLayout.setContentsMargins(12, 8, 12, 8)

        # Bit 位多选下拉框 — 移动类型
        self._move_combo = BitComboBox("type", values=[], sep="")
        self._move_combo.setFixedWidth(144)

        # 地形适性微调框 × 4
        _adapt_mapping = EnumData().ROBOT["ADAPT"]

        self._air_label = BodyLabel(self.tr("air"), self._terrain_card)
        self._air_spin = MappingCompSpin("air", mapping=_adapt_mapping, parent=self._terrain_card)
        self._air_spin.setFixedWidth(100)

        self._grd_label = BodyLabel(self.tr("ground"), self._terrain_card)
        self._grd_spin = MappingCompSpin("grd", mapping=_adapt_mapping, parent=self._terrain_card)
        self._grd_spin.setFixedWidth(100)

        self._wtr_label = BodyLabel(self.tr("water"), self._terrain_card)
        self._wtr_spin = MappingCompSpin("wtr", mapping=_adapt_mapping, parent=self._terrain_card)
        self._wtr_spin.setFixedWidth(100)

        self._spc_label = BodyLabel(self.tr("space"), self._terrain_card)
        self._spc_spin = MappingCompSpin("spc", mapping=_adapt_mapping, parent=self._terrain_card)
        self._spc_spin.setFixedWidth(100)

        _grid = QGridLayout()
        _grid.setSpacing(4)
        _grid.addWidget(self._move_combo, 0, 0, 1, 2, Qt.AlignmentFlag.AlignRight)
        _grid.addWidget(self._air_label, 1, 0)
        _grid.addWidget(self._air_spin, 1, 1)
        _grid.addWidget(self._grd_label, 2, 0)
        _grid.addWidget(self._grd_spin, 2, 1)
        _grid.addWidget(self._wtr_label, 3, 0)
        _grid.addWidget(self._wtr_spin, 3, 1)
        _grid.addWidget(self._spc_label, 4, 0)
        _grid.addWidget(self._spc_spin, 4, 1)
        self._terrain_card.viewLayout.addLayout(_grid)
        self._terrain_card.viewLayout.addStretch()

        # ========== 布局 ==========

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(self._terrain_card)
        layout.addStretch()

        self.setLayout(layout)

        # 触发初始翻译
        self.translateUI()

    # ========== 翻译 ==========

    def translateUI(self):
        """刷新卡片标题、标签文本及下拉选项"""
        self._terrain_card.setTitle(self.tr("Terrain"))
        # EnumData 在构造时缓存了 tr() 结果，每次刷新重新创建以获取新翻译
        _enum = EnumData()
        self._move_combo.set_values(_enum.ROBOT["MOVETYPE"])
        self._air_label.setText(self.tr("air"))
        self._air_spin.set_mapping(_enum.ROBOT["ADAPT"])
        self._grd_label.setText(self.tr("ground"))
        self._grd_spin.set_mapping(_enum.ROBOT["ADAPT"])
        self._wtr_label.setText(self.tr("water"))
        self._wtr_spin.set_mapping(_enum.ROBOT["ADAPT"])
        self._spc_label.setText(self.tr("space"))
        self._spc_spin.set_mapping(_enum.ROBOT["ADAPT"])

    # ========== 主题刷新 ==========

    def resetUI(self):
        """刷新主框字体"""
        self._move_combo.resetUI()
        super().resetUI()

    # ========== 行数据 ==========

    def set_row_data(self, data: dict) -> None:
        """选中行数据变更时刷新所有子编辑器

        Args:
            data: 当前选中行的数据字典
        """
        self._move_combo.set_data(data)
        self._air_spin.set_data(data)
        self._grd_spin.set_data(data)
        self._wtr_spin.set_data(data)
        self._spc_spin.set_data(data)

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
