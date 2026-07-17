"""
固定行数表格模型 - 行数不可增删、支持原地编辑

在 BaseTableModel 基础上增加 ItemIsEditable 标志，
编辑器类型由外部 Delegate 决定。

Classes:
    FixedTableModel: 固定行数表格模型
"""

from typing import Any

from PySide6.QtCore import QModelIndex, Qt

from .base_model import BaseTableModel


class FixedTableModel(BaseTableModel):
    """固定行数表格模型 - 行数不可增删，支持原地编辑"""

    # ========== Qt 模型接口重写 ==========

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """按链路 列索引 → 表头 → key → row dict 取值

        Args:
            index: 数据索引
            role: DisplayRole 经格式化函数转换后返回，
                  EditRole 返回原始值，其余返回 None

        Returns:
            单元格显示或编辑用的数据
        """
        if self._fields is None:
            raise RuntimeError("没有传入映射类")
        if not index.isValid():
            return None
        header = self._headers[index.column()]
        key = self._fields.get_field(header)
        value = self._data[index.row()].get(key)

        if role == Qt.ItemDataRole.DisplayRole:
            display_fn = self._titles[header][0] if header in self._titles else None
            return display_fn(value) if display_fn else value

        if role == Qt.ItemDataRole.EditRole:
            return value

        if role == Qt.ItemDataRole.FontRole:
            return self._get_font(index.column())

        return None

    def setData(
        self,
        index: QModelIndex,
        value: Any,
        role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        """按链路 列索引 → 表头 → key → row dict 设值

        Args:
            index: 数据索引
            value: 要写入的值
            role: 仅处理 EditRole

        Returns:
            写入成功返回 True
        """
        if self._fields is None:
            raise RuntimeError("未设定全局字段映射")

        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False
        header = self._headers[index.column()]
        key = self._fields.get_field(header)
        self._data[index.row()][key] = value
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])
        return True

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """允许原地编辑

        Args:
            index: 数据索引

        Returns:
            含 ItemIsEditable 的标志组合
        """
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEditable
