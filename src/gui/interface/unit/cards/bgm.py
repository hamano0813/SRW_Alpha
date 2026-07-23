"""
BGM 卡片

BGM 选择下拉框，中日界面使用日语字体。
"""

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy
from qfluentwidgets import qconfig, setFont

from config import option
from gui.custom.enums import EnumData
from gui.custom.fonts import JP_FONT, JP_QFONT
from gui.widget import CardHeader, CommonMappingCombo, CommonStretchLabel


class BgmCard(CardHeader):
    """BGM 卡片 - BGM 选择下拉框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("BGM")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        _bgm_mapping = EnumData().BGM
        self._bgm_label = CommonStretchLabel(self.tr("Music"), self)
        self._bgm_label.setFixedWidth(60)
        self._bgm_combo = CommonMappingCombo(mapping=_bgm_mapping, parent=self)
        self._apply_bgm_font()

    def _apply_bgm_font(self):
        lang = qconfig.get(option.language)
        if lang in ("zh_CN", "ja_JP"):
            self._bgm_combo.apply_font(JP_FONT)
            self._bgm_combo.set_dropdown_font(JP_QFONT)
        self._bgm_combo.valueChanged.connect(lambda v: self._write("bgm", v))

        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        row.addWidget(self._bgm_label)
        row.addWidget(self._bgm_combo, 1)
        self.viewLayout.addLayout(row)

    def set_row(self, row: int) -> None:
        super().set_row(row)
        self._bgm_combo.set_value(self._read("bgm"))

    def translateUI(self) -> None:
        self._bgm_label.setText(self.tr("Music"))
        self._bgm_combo.set_mapping(EnumData().BGM)

    def resetUI(self) -> None:
        self._bgm_combo.resetUI()
        self._apply_bgm_font()
        setFont(self)
        setFont(self.headerLabel, 15, QFont.Weight.DemiBold)
        setFont(self._bgm_label)
