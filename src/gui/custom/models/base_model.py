"""
表格模型共用基类 - 封装字段映射与标题管理

提供 set_data() 装入数据、set_title() 设置列标题与格式化函数、
set_field() 设置字段映射查询器。
子类 data() 中通过 FieldMapping.get_field(header) 获取数据 key。

Classes:
    BaseTableModel: 表格模型基类
"""

from typing import Any, Callable

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QFont

from gui.custom.fields import FieldMapping


class BaseTableModel(QAbstractTableModel):
    """表格模型基类 - 封装字段映射、数据装入和标题管理

    初始化时不带数据；set_data() / set_title() 均可在运行期重复调用。
    """

    class IndexMode:
        """垂直行号的索引显示模式"""

        HEX = 1
        DEC = 0

    def __init__(self, parent=None):
        """初始化空模型

        Args:
            parent: 父 QObject
        """
        super().__init__(parent)
        self._data: list[dict[str, Any]] = []  # 行数据列表
        self._fields: FieldMapping | None = None  # 列名映射查询器
        self._titles: dict[str, list[Callable | None]] = {}  # {tr(表头): [格式化函数, 反解析函数]}
        self._headers: list[str] = []  # 有序表头列表（列索引 → 表头）
        self._index = BaseTableModel.IndexMode.HEX
        self._width: int = 0
        self._fonts: dict = {}  # 自定义字体

    # ========== 公开接口 ==========

    def set_field(self, fields: FieldMapping) -> None:
        """设置字段映射查询器

        提供翻译后表头 → 数据 key 的查询能力。
        必须在各 _init_* 使用前调用，通常在构造后立即设置。

        Args:
            fields: FieldMapping 实例
        """
        self._fields = fields

    def set_data(self, data: list[dict[str, Any]]) -> None:
        """装入列表数据

        Args:
            data: 行数据列表，每项为一个 dict，key 与 set_title 的 value 对应
        """
        self.beginResetModel()
        self._data = data
        if self._index == BaseTableModel.IndexMode.HEX:
            self._width = len(f"{len(data):0X}")
        self.endResetModel()

    def set_title(self, titles: dict[str, list[Callable | None]]) -> None:
        """设置列标题与字段映射

        Args:
            titles: {tr(表头文字): [格式化函数, 反解析函数], ...}
                    key 已通过 self.tr() 翻译完成，_fields 直接存储
                    value[0] = display 函数（原始值 → 显示文本），EditRole 仍然返回原始值
                    value[1] = parse 函数（显示文本 → 原始值），供批量粘贴等场景
        """
        self.beginResetModel()
        self._titles = titles
        self._headers = list(titles.keys())
        self.endResetModel()

    def set_font(self, fonts: dict) -> None:
        """设置列字体映射

        Args:
            fonts: {列号: font_dict}，-1 表示全局默认
        """
        self._fonts = fonts

    # ========== Qt 模型接口 ==========

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """返回数据行数"""
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """返回列数"""
        return len(self._headers)

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """返回列标题或垂直行号

        Args:
            section: 节编号
            orientation: 水平=列标题，垂直=行号
            role: DisplayRole 返回文字，TextAlignmentRole 返回居中

        Returns:
            表头文字或对齐标志
        """
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._headers[section]
            elif orientation == Qt.Orientation.Vertical:
                if self._width > 0:
                    return f"[{section:0{self._width}X}]"
                else:
                    return f"{section + 1:d}"
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        return None

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """子类重写此方法返回指定角色的数据

        Args:
            index: 数据索引
            role: 数据角色

        Returns:
            对应角色的数据，默认返回 None
        """
        return None

    def setData(
        self,
        index: QModelIndex,
        value: Any,
        role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        """子类重写此方法写入指定角色的数据

        Args:
            index: 数据索引
            value: 要写入的值
            role: 数据角色

        Returns:
            写入成功返回 True
        """
        return True

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """子类重写此方法返回单元格标志

        Args:
            index: 数据索引

        Returns:
            单元格 ItemFlag
        """
        return Qt.ItemFlag.ItemIsSelectable

    # ========== 工具方法 ==========

    def get_row_data(self, row: int) -> dict[str, Any]:
        """获取指定行的原始 dict 数据

        Args:
            row: 行号

        Returns:
            该行的数据 dict
        """
        return self._data[row]

    def _get_font(self, column: int) -> QFont | None:
        """按列号查询字体配置，无配置时返回 None

        优先查 column 指定列，回退到 -1（全局默认）。

        Args:
            column: 列号

        Returns:
            构造好的 QFont，或 None
        """
        font_dict = self._fonts.get(column) or self._fonts.get(-1)
        if font_dict is None:
            return None
        family = font_dict.get("family")
        size = font_dict.get("size")
        weight = font_dict.get("weight")
        italic = font_dict.get("italic")
        font = QFont(family)
        if size:
            font.setPixelSize(size)
        if weight:
            font.setWeight(weight)
        if italic:
            font.setItalic(italic)
        return font
