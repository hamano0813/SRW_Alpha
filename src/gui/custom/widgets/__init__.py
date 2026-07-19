"""
编辑器控件包

按用途拆分为两个子包：
  - table/    表格内的编辑器控件（TableEditor 子类，供 delegates 使用）
  - panel/    面板上的搜索/过滤/定位控件（待填充）
  - spin_box  独立微调框组件（FluentIcon 箭头，可复用于映射/数值微调）

顶层 re-export table 子包的所有导出，保持已有 imports 向后兼容。

Subpackages:
    table: 表格编辑器控件
    panel: 面板控件（待实现）
"""

from .panel import BitComboBox, MappingComboBox, MappingCompSpin, NumberCompSpin, PanelEditor
from .table import MappingSpinBox, MultiLineEdit, NumberSpinBox, SingleLineEdit, TableEditor

__all__ = [
    "TableEditor",
    "SingleLineEdit",
    "MultiLineEdit",
    "NumberSpinBox",
    "MappingSpinBox",
    "PanelEditor",
    "BitComboBox",
    "MappingCompSpin",
    "MappingComboBox",
    "NumberCompSpin",
]
