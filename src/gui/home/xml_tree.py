"""
XML 项目文件目录树

以 QTreeWidget 展示 cache.xml 中 directory_tree 的目录文件层级。
提供对 PS1 ISO 文件系统的可视化浏览。

Classes:
    XmlTreeView: XML 目录树视图
"""

import os
import xml.etree.ElementTree as ET

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHeaderView, QTreeWidgetItem
from qfluentwidgets import TreeWidget, getFont, setCustomStyleSheet


class XmlTreeView(TreeWidget):
    """XML 目录树视图 - 展示 cache.xml 中 directory_tree 下的文件层级"""

    def __init__(self, headers: list, datas: dict, parent=None):
        super().__init__(parent)
        self._headers = headers
        self._datas = datas
        self.setHeaderLabels(headers)
        self.setAnimated(True)
        self.setSelectionMode(TreeWidget.SelectionMode.SingleSelection)

        # 列宽：首列 200，后续每列 100
        header = self.header()
        for i in range(len(headers)):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Fixed)
            self.setColumnWidth(i, 200 if i == 0 else 100)

        self.itemDoubleClicked.connect(self._on_item_double_clicked)

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """双击项目时的临时调试输出，后续可替换为编辑功能"""
        tag = item.data(0, Qt.ItemDataRole.UserRole) or "unknown"
        name = item.text(0) or "(unnamed)"
        print(f"[XmlTreeView] double-clicked: tag={tag}, name={name}, column={column}")

    def load_xml(self, xml_path: str) -> bool:
        """加载 cache.xml 并展开 directory_tree 子树

        Args:
            xml_path: cache.xml 文件路径

        Returns:
            加载成功返回 True，否则返回 False
        """
        self.clear()

        if not os.path.isfile(xml_path):
            return False

        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # 定位到 directory_tree 节点，只展示该子树
            dir_tree = root.find(".//directory_tree")
            if dir_tree is None:
                return False

            # 将 directory_tree 的所有子节点作为顶层项
            self._build_children(dir_tree, None)
            self.expandToDepth(1)
            return True
        except ET.ParseError:
            return False

    def _build_children(self, element: ET.Element, parent_item: QTreeWidgetItem | None):
        """遍历 XML 子节点并逐一构建树项"""
        for child in element:
            self._build_tree(child, parent_item)

    def _build_tree(self, element: ET.Element, parent_item: QTreeWidgetItem | None):
        """递归构建 XML 节点为树项

        file 节点在第 0 列显示文件名，按 _datas 匹配后在第 N 列打勾，末列省略；
        dir 节点在第 0 列显示目录名；其余标签回退显示标签名。
        """
        attrib = dict(element.attrib)
        tag = element.tag

        n = len(self._headers)
        cols = [""] * n

        if tag == "file":
            file_name = attrib.get("name", "")
            cols[0] = file_name

            # 检查文件名是否匹配某类别，匹配则在对应列打 ✓
            for col_header, file_list in self._datas.items():
                if file_name in file_list:
                    try:
                        col_idx = self._headers.index(col_header)
                        cols[col_idx] = "🗸"
                    except ValueError:
                        pass

        elif tag == "dir":
            cols[0] = attrib.get("name", "")
        else:
            cols[0] = tag

        item = QTreeWidgetItem(parent_item or self, cols)
        item.setData(0, Qt.ItemDataRole.UserRole, tag)
        for col_idx in range(n):
            if col_idx:
                item.setData(col_idx, Qt.ItemDataRole.FontRole, getFont(18, QFont.Weight.Bold))
                item.setData(col_idx, Qt.ItemDataRole.TextAlignmentRole, Qt.AlignmentFlag.AlignCenter)
            else:
                item.setData(col_idx, Qt.ItemDataRole.FontRole, getFont(14))

        for child in element:
            self._build_tree(child, item)

    def clear_xml(self):
        """清空当前树视图"""
        self.clear()

    def resetUI(self):
        """刷新界面字体 — 用 QSS 覆盖 qfluentwidgets 默认表头字号"""
        qss = "QHeaderView::section { font-size: 16px; font-weight: bold;}"
        setCustomStyleSheet(self, qss, qss)
