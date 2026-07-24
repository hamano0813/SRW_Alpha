"""
驾驶员等级制技能卡片

提供 3 条成长型技能的表格编辑（USKILL 类型 + Lv1-Lv9 等级）。
Lv 列用 NumberSpinDelegate（0-99，无按钮，键盘输入），0 存为 0xFF。
"""

from typing import Any

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtWidgets import QFrame, QHeaderView, QSizePolicy, QWidget

from gui.custom import EnumData, FieldMapping
from gui.widget import CardHeader, FixedTableView, MappingSpinDelegate, NumberSpinDelegate


class _LvDelegate(NumberSpinDelegate):
    """Lv 等级列委托 - 0-99 键盘输入，0 存为 0xFF，0xFF 显示"－" """

    def __init__(self, parent=None):
        super().__init__(value_range=(0, 99), show_buttons=False, read_only=False, parent=parent)

    def format_display(self, value) -> str:
        if value is None:
            return ""
        return "－" if int(value) == 0xFF else str(int(value))

    def parse_display(self, text: str) -> Any:
        if text.strip() == "－":
            return 0xFF
        try:
            return int(text)
        except (ValueError, TypeError):
            return 0xFF

    def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:
        super().setEditorData(editor, index)
        value = index.data(Qt.ItemDataRole.EditRole)
        editor.set_value(0 if value == 0xFF else int(value))

    def setModelData(self, editor: QWidget, model, index: QModelIndex) -> None:
        raw = editor.get_value()
        model.setData(index, 0xFF if raw == 0 else int(raw))


class UpgradedSkillsCard(CardHeader):
    """等级制技能卡片 - 自含技能等级编辑表格"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setTitle(self.tr("Upgraded skills"))
        self.viewLayout.setContentsMargins(0, 0, 0, 0)

        # ========== 映射表 ==========

        self._skill_fields = FieldMapping()

        # ========== 表格 ==========

        self._table = FixedTableView(self)
        self._table.setFixedHeight(150)
        _model = self._table.source_model()
        _model.set_field(self._skill_fields)

        # ========== 委托 ==========

        self._sname_delegate = MappingSpinDelegate(
            mapping=EnumData().PILOT["USKILL"], wrapping=True, parent=self._table,
        )
        self._table.setItemDelegateForColumn(0, self._sname_delegate)

        self._lv_delegates = [_LvDelegate(parent=self._table) for _ in range(9)]
        for i in range(9):
            self._table.setItemDelegateForColumn(i + 1, self._lv_delegates[i])

        # ========== 列标题与格式化 ==========

        titles = {
            self.tr("Skill name"): [
                self._sname_delegate.format_display,
                self._sname_delegate.parse_display,
            ],
        }
        for i in range(9):
            lv_key = f"Lv{i + 1}"
            titles[self.tr(lv_key)] = [
                self._lv_delegates[i].format_display,
                self._lv_delegates[i].parse_display,
            ]
        _model.set_title(titles)

        # ========== 对齐 ==========

        _alignments = {0: Qt.AlignmentFlag.AlignCenter}
        for i in range(9):
            _alignments[i + 1] = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        _model.set_alignments(_alignments)

        # ========== 外观 ==========

        self._widths = [158] + [54] * 9
        self._table.setShowGrid(False)
        self._table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._table.verticalHeader().setVisible(False)
        self._table.setTextElideMode(Qt.TextElideMode.ElideNone)
        self._table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self._table.setFrameShape(QFrame.Shape.NoFrame)
        self._table.horizontalHeader().setStretchLastSection(False)
        self._table.verticalHeader().setFixedWidth(30)
        self._table.verticalHeader().setMinimumSectionSize(28)
        self._table._corner_button.setVisible(False)

        # ========== 数据变更写回 ==========

        _model.dataChanged.connect(self._on_data_changed)

        self.viewLayout.addWidget(self._table)

    # ========== 数据 ==========

    def set_row(self, row: int) -> None:
        super().set_row(row)
        sklu = self._read("sklu")
        if sklu is None:
            _empty = {"sname": 0xFF, "l1": 0xFF, "l2": 0xFF, "l3": 0xFF,
                      "l4": 0xFF, "l5": 0xFF, "l6": 0xFF, "l7": 0xFF, "l8": 0xFF, "l9": 0xFF}
            sklu = [_empty.copy() for _ in range(3)]
        self._table.set_data(sklu)
        if self._widths:
            self._table.set_column_width(self._widths)

    def _on_data_changed(self) -> None:
        _model = self._table.source_model()
        self._write("sklu", _model.get_data())

    # ========== 翻译与字体 ==========

    def translateUI(self) -> None:
        self.setTitle(self.tr("Upgraded skills"))
        self._skill_fields.translateUI()

        self._sname_delegate = MappingSpinDelegate(
            mapping=EnumData().PILOT["USKILL"], wrapping=True, parent=self._table,
        )
        self._table.setItemDelegateForColumn(0, self._sname_delegate)

        titles = {
            self.tr("Skill name"): [
                self._sname_delegate.format_display,
                self._sname_delegate.parse_display,
            ],
        }
        for i in range(9):
            lv_key = f"Lv{i + 1}"
            titles[self.tr(lv_key)] = [
                self._lv_delegates[i].format_display,
                self._lv_delegates[i].parse_display,
            ]
        self._table.source_model().set_title(titles)

    def resetUI(self) -> None:
        self._table.resetUI()
