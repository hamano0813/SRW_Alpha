"""
机体侧边栏面板 - 分组卡片布局与数据编辑

提供机体数据的编辑和搜索功能。继承 ProxyFrame，
自动传播 resetUI / translateUI 至子控件。

Classes:
    UnitPanel: 机体侧边栏面板
"""

from PySide6.QtCore import Qt, QEasingCurve, QPropertyAnimation, Signal
from PySide6.QtWidgets import QGridLayout, QVBoxLayout

from gui.custom import fonts
from gui.custom.enums import EnumData
from gui.custom.proxy_frame import ProxyFrame
from gui.custom.widgets import BitComboBox, MappingCompSpin
from qfluentwidgets import BodyLabel, HeaderCardWidget


class UnitPanel(ProxyFrame):
    """机体侧边栏面板 - 分组卡片编辑区"""

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

        # ========== 地形适性卡片 ==========

        self._terrain_card = HeaderCardWidget(self)
        self._terrain_card.setTitle(self.tr("Terrain"))
        self._terrain_card.setBorderRadius(8)
        self._terrain_card.setMaximumWidth(220)
        self._terrain_card.viewLayout.setContentsMargins(12, 8, 12, 8)

        # Bit 位多选下拉框 — 移动类型
        self._move_combo = BitComboBox("type", values=[], sep="")
        self._move_combo.setFixedWidth(144)
        self._move_combo.apply_font(fonts.JP_QFONT)
        self._move_combo.dataChanged.connect(lambda _: self.panelDataChanged.emit("type"))

        # 地形适性微调框 × 4
        _adapt_mapping = EnumData().ROBOT["ADAPT"]
        _adapt_fields = ["air", "grd", "wtr", "spc"]
        _adapt_labels = [self.tr("Air"), self.tr("Grd"), self.tr("Wtr"), self.tr("Spc")]

        self._adapt_spins: dict[str, tuple[BodyLabel, MappingCompSpin]] = {}
        for i, (field, label) in enumerate(zip(_adapt_fields, _adapt_labels)):
            lbl = BodyLabel(label, self._terrain_card)
            spin = MappingCompSpin(field, mapping=_adapt_mapping, parent=self._terrain_card)
            spin.setFixedWidth(100)
            spin.dataChanged.connect(lambda _, f=field: self.panelDataChanged.emit(f))
            self._adapt_spins[field] = (lbl, spin)

        _grid = QGridLayout()
        _grid.setSpacing(4)
        _grid.addWidget(self._move_combo, 0, 0, 1, 2, Qt.AlignmentFlag.AlignRight)
        for i, field in enumerate(_adapt_fields, start=1):
            lbl, spin = self._adapt_spins[field]
            _grid.addWidget(lbl, i, 0)
            _grid.addWidget(spin, i, 1)
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
        for field, (lbl, spin) in self._adapt_spins.items():
            spin.set_mapping(_enum.ROBOT["ADAPT"])

    # ========== 行数据 ==========

    def set_row_data(self, data: dict) -> None:
        """选中行数据变更时刷新所有子编辑器

        Args:
            data: 当前选中行的数据字典
        """
        self._move_combo.set_data(data)
        for field, (_, spin) in self._adapt_spins.items():
            spin.set_data(data)

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
