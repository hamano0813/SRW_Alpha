"""
ROM 文件与编辑项目对应表

展示各 ROM 文件与编辑项目（机体、驾驶员、文本等）之间的对应关系。
继承 qfluentwidgets 的 TableWidget，自带 Fluent Design 样式。

Classes:
    FileTable: ROM 文件 × 编辑项目 对应表
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHeaderView, QTableWidgetItem
from qfluentwidgets import TableWidget


class FileTable(TableWidget):
    """ROM 文件 × 编辑项目 对应表"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_table()

        self.setSelectionMode(TableWidget.SelectionMode.SingleSelection)
        self.cellDoubleClicked.connect(self._on_double_clicked)

    def _build_table(self):
        """构建表格结构：表头 → 行数据 → 列宽策略"""
        headers = [
            self.tr("File"),
            self.tr("Unit"),
            self.tr("Pilot"),
            self.tr("Text"),
            self.tr("Scenario"),
            self.tr("Intermission"),
            self.tr("Character"),
            self.tr("Other"),
        ]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)

        rows = [
            ("ROBOT.RAF",          ["✓", "",  "",  "✓", "",  "",  ""]),
            ("PILOT.RAF",          ["",  "✓", "",  "✓", "",  "",  ""]),
            ("SNMSG.BIN",          ["",  "",  "✓", "✓", "",  "",  ""]),
            ("SNDATA.BIN",         ["",  "",  "",  "✓", "",  "",  ""]),
            ("ENLIST.BIN",         ["",  "",  "",  "✓", "",  "",  ""]),
            ("AIUNP.BIN",          ["",  "",  "",  "✓", "",  "",  ""]),
            ("SCRIPT.BIN",         ["",  "",  "",  "",  "✓", "",  ""]),
            ("PRM_GRP.BIN",        ["",  "",  "",  "",  "",  "",  "✓"]),
            ("12F.DAT",            ["",  "",  "",  "",  "",  "✓", ""]),
        ]

        self.setRowCount(len(rows))
        for row_idx, (file_name, checks) in enumerate(rows):
            file_item = QTableWidgetItem(file_name)
            file_item.setFlags(file_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(row_idx, 0, file_item)

            for col_idx, val in enumerate(checks):
                item = QTableWidgetItem(val)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.setItem(row_idx, col_idx + 1, item)

        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for col in range(1, len(headers)):
            self.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.ResizeToContents)
        self.setEditTriggers(TableWidget.EditTrigger.NoEditTriggers)
        self.setSelectionBehavior(TableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(TableWidget.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setHidden(True)

    def _on_double_clicked(self, row: int, column: int):
        """双击行时打印文件路径（暂为占位，后续替换为打开文件夹）"""
        file_name = self.item(row, 0).text()
        print(f"Open folder for: {file_name}")

    def translateUI(self):
        """刷新表头翻译"""
        self._build_table()
