"""
变形·合体卡片

提供变形组、变形序号、合体组、合体序号、合体数量、核心机体、机体换装编辑。
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGridLayout
from qfluentwidgets import setFont

from gui.custom import EnumData, JP_FONT, JP_QFONT
from gui.widget import (
    BaseTableModel,
    CardHeader,
    CommonMappingCombo,
    CommonNumberSpin,
    CommonStretchLabel,
    RobotCombo,
)


class TransformCard(CardHeader):
    """变形·合体卡片 - 变形组与变形序号"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Transform & Combine"))

        _align = Qt.AlignmentFlag.AlignCenter

        self._lbl_tgrp = CommonStretchLabel(self.tr("Tran Grp"), self)
        self._lbl_tgrp.setAlignment(_align)
        self._tgrp_spin = CommonNumberSpin(value_range=(0, 99), parent=self)
        self._tgrp_spin.valueChanged.connect(lambda v: self._write("tgrp", v))

        self._lbl_tsn = CommonStretchLabel(self.tr("Tran Seq"), self)
        self._lbl_tsn.setAlignment(_align)
        self._tsn_spin = CommonNumberSpin(value_range=(0, 2), parent=self)
        self._tsn_spin.valueChanged.connect(lambda v: self._write("tsn", v))

        self._lbl_cgrp = CommonStretchLabel(self.tr("Comb Grp"), self)
        self._lbl_cgrp.setAlignment(_align)
        self._cgrp_spin = CommonNumberSpin(value_range=(0, 99), parent=self)
        self._cgrp_spin.valueChanged.connect(lambda v: self._write("cgrp", v))

        self._lbl_csn = CommonStretchLabel(self.tr("Comb Seq"), self)
        self._lbl_csn.setAlignment(_align)
        self._csn_spin = CommonNumberSpin(value_range=(0, 2), parent=self)
        self._csn_spin.valueChanged.connect(lambda v: self._write("csn", v))

        self._lbl_cnt = CommonStretchLabel(self.tr("Comb Cnt"), self)
        self._lbl_cnt.setAlignment(_align)
        self._cnt_spin = CommonNumberSpin(value_range=(0, 5), parent=self)
        self._cnt_spin.valueChanged.connect(lambda v: self._write("count", v))

        self._lbl_core = CommonStretchLabel(self.tr("Core Unit"), self)
        self._lbl_core.setAlignment(_align)
        self._core_combo = RobotCombo(parent=self, supplements={0xFFFF: "——"})
        self._core_combo.valueChanged.connect(lambda v: self._write("core", v))

        self._lbl_option = CommonStretchLabel(self.tr("Unit Opt"), self)
        self._lbl_option.setAlignment(_align)
        _option_mapping = EnumData().ROBOT["OPTION"]
        self._option_combo = CommonMappingCombo(mapping=_option_mapping, parent=self)
        self._option_combo.apply_font(JP_FONT)
        self._option_combo.set_dropdown_font(JP_QFONT)
        self._option_combo.valueChanged.connect(lambda v: self._write("option", v))

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

    def set_model(self, model: BaseTableModel) -> None:
        super().set_model(model)
        self._core_combo.register()

    def set_row(self, row: int) -> None:
        super().set_row(row)
        self._tgrp_spin.set_value(self._read("tgrp"))
        self._tsn_spin.set_value(self._read("tsn"))
        self._cgrp_spin.set_value(self._read("cgrp"))
        self._csn_spin.set_value(self._read("csn"))
        self._cnt_spin.set_value(self._read("count"))
        self._core_combo.set_value(self._read("core"))
        self._option_combo.set_value(self._read("option"))

    def translateUI(self) -> None:
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
        self._tgrp_spin.resetUI()
        self._tsn_spin.resetUI()
        self._cgrp_spin.resetUI()
        self._csn_spin.resetUI()
        self._cnt_spin.resetUI()
        self._option_combo.resetUI()
        self._option_combo.apply_font(JP_FONT)
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
        setFont(self._lbl_tgrp)
        setFont(self._lbl_tsn)
        setFont(self._lbl_cgrp)
        setFont(self._lbl_csn)
        setFont(self._lbl_cnt)
        setFont(self._lbl_core)
        setFont(self._lbl_option)
