"""
驾驶员详细信息卡片

提供驾驶员全名、性格、SP、气力组、二回行动等基本属性的编辑。
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGridLayout, QLineEdit, QSizePolicy
from qfluentwidgets import BodyLabel, setFont

from gui.custom import EnumData
from gui.widget import CardHeader, CommonMappingCombo, CommonNumberSpin, LevelSpin

_EMPTY_VALUE = 0xFF  # LevelSpin 的空值标记


class PilotDetailCard(CardHeader):
    """驾驶员详细信息卡片 - 全名、性格、SP、气力组、二回行动"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setTitle(self.tr("Pilot Detail"))

        grid = QGridLayout()
        grid.setSpacing(8)

        # ========== 第 0 行：全名 + 性格 ==========

        self._fname_label = BodyLabel(self.tr("Fullname"), self)
        self._fname_label.setMinimumWidth(80)
        self._fname_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._fname_edit = QLineEdit(self)
        self._fname_edit.setFixedHeight(33)
        setFont(self._fname_edit, 14)
        self._fname_edit.setStyleSheet("QLineEdit { padding-left: 10px; }")
        self._fname_edit.textChanged.connect(lambda t: self._write("fname", t))

        self._pers_label = BodyLabel(self.tr("Personality"), self)
        self._pers_label.setMinimumWidth(80)
        self._pers_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._pers_combo = CommonMappingCombo(mapping=EnumData().PILOT["PERSONALITY"], parent=self)
        self._pers_combo.setMinimumWidth(155)
        self._pers_combo.valueChanged.connect(lambda v: self._write("pers", v))

        grid.addWidget(self._fname_label, 0, 0)
        grid.addWidget(self._fname_edit, 0, 1, 1, 3)
        grid.addWidget(self._pers_label, 0, 4)
        grid.addWidget(self._pers_combo, 0, 5)

        # ========== 第 1 行：二回行动 + SP + 气力组 ==========

        self._daction_label = BodyLabel(self.tr("D.Action"), self)
        self._daction_label.setMinimumWidth(80)
        self._daction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._daction_spin = LevelSpin(self)
        self._daction_spin.setRange(0, 100)
        self._daction_spin.valueChanged.connect(lambda v: self._write("daction", 0 if v == _EMPTY_VALUE else v))

        self._sp_label = BodyLabel(self.tr("SP"), self)
        self._sp_label.setMinimumWidth(80)
        self._sp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sp_spin = CommonNumberSpin(value_range=(0, 255), parent=self)
        self._sp_spin.valueChanged.connect(lambda v: self._write("sp", v))

        self._fsg_label = BodyLabel(self.tr("Friendship"), self)
        self._fsg_label.setMinimumWidth(80)
        self._fsg_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._fsg_spin = CommonNumberSpin(value_range=(0, 255), parent=self)
        self._fsg_spin.valueChanged.connect(lambda v: self._write("fsg", v))

        grid.addWidget(self._daction_label, 1, 0)
        grid.addWidget(self._daction_spin, 1, 1)
        grid.addWidget(self._sp_label, 1, 2)
        grid.addWidget(self._sp_spin, 1, 3)
        grid.addWidget(self._fsg_label, 1, 4)
        grid.addWidget(self._fsg_spin, 1, 5)

        # 第 1 行与第 0 行的输入框列宽同步
        grid.setColumnStretch(0, 0)   # 标签不拉伸
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(2, 0)   # 标签不拉伸
        grid.setColumnStretch(3, 1)
        grid.setColumnStretch(4, 0)   # 标签不拉伸
        grid.setColumnStretch(5, 1)

        self.viewLayout.addLayout(grid)

    def set_row(self, row: int) -> None:
        super().set_row(row)
        fname = self._read("fname") or ""
        self._fname_edit.blockSignals(True)
        self._fname_edit.setText(fname)
        self._fname_edit.blockSignals(False)

        self._pers_combo.set_value(self._read("pers") or 0)

        daction = self._read("daction") or 0
        self._daction_spin.set_value(_EMPTY_VALUE if daction == 0 else daction)

        self._sp_spin.set_value(self._read("sp") or 0)
        self._fsg_spin.set_value(self._read("fsg") or 0)

    def translateUI(self) -> None:
        self.setTitle(self.tr("Pilot Detail"))
        self._fname_label.setText(self.tr("Fullname"))
        self._pers_label.setText(self.tr("Personality"))
        self._pers_combo.set_mapping(EnumData().PILOT["PERSONALITY"])
        self._daction_label.setText(self.tr("D.Action"))
        self._sp_label.setText(self.tr("SP"))
        self._fsg_label.setText(self.tr("Friendship"))

    def resetUI(self) -> None:
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
        setFont(self._fname_edit, 14)
        setFont(self._fname_label)
        setFont(self._pers_label)
        setFont(self._daction_label)
        setFont(self._sp_label)
        setFont(self._fsg_label)
        self._daction_spin.resetUI()
        self._pers_combo.resetUI()
        self._sp_spin.resetUI()
        self._fsg_spin.resetUI()

