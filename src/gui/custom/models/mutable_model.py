"""
可增删表格模型 - 行数可变、弹窗编辑

在 BaseTableModel 基础上增加行插入/删除/追加操作。
单元格不可原地编辑（flags 不返回 ItemIsEditable），
编辑由外部弹窗处理。

Classes:
    MutableTableModel: 可增删表格模型
"""

from typing import Any

from PySide6.QtCore import QModelIndex, Qt

from .base_model import BaseTableModel


class MutableTableModel(BaseTableModel):
    """可增删行数表格模型 - 支持行插入/删除/追加

    单元格不返回 ItemIsEditable，编辑由外部弹窗处理。
    """

    # ========== 行增删 ==========

    def insert_row(self, row: int, data: dict[str, Any] | None = None) -> bool:
        """在指定位置插入一行

        Args:
            row:  插入位置（0 ~ rowCount()）
            data: 行数据，为 None 时以空字符串填充各字段

        Returns:
            是否成功
        """
        if self._fields is None:
            raise RuntimeError("未设定全局字段映射")

        if row < 0 or row > len(self._data):
            return False
        if data is None:
            data = {self._fields.get_field(h): "" for h in self._headers}
        self.beginInsertRows(QModelIndex(), row, row)
        self._data.insert(row, data)
        self.endInsertRows()
        return True

    def remove_row(self, row: int) -> bool:
        """删除指定行

        Args:
            row: 要删除的行号

        Returns:
            是否成功
        """
        if row < 0 or row >= len(self._data):
            return False
        self.beginRemoveRows(QModelIndex(), row, row)
        del self._data[row]
        self.endRemoveRows()
        return True

    def append_row(self, data: dict[str, Any] | None = None) -> bool:
        """在末尾追加一行

        Args:
            data: 行数据，为 None 时以空字符串填充各字段

        Returns:
            是否成功
        """
        return self.insert_row(len(self._data), data)

    # ========== Qt 模型接口重写 ==========

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """按链路 列索引 → 表头 → key → row dict 取值

        Args:
            index: 数据索引
            role: DisplayRole/EditRole 返回原始值，其余返回 None

        Returns:
            单元格显示或编辑用的原始数据
        """
        if not index.isValid():
            return None
        header = self._headers[index.column()]
        key = self._fields.get_field(header)
        value = self._data[index.row()].get(key)
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            return value
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """禁止原地编辑——不返回 ItemIsEditable

        Args:
            index: 数据索引

        Returns:
            不含 ItemIsEditable 的标志组合
        """
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
