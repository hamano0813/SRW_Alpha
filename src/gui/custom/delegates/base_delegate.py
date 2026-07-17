"""
单元格委托基类 - 封装 DataWidget 与 QStyledItemDelegate 的标准交互

子类只需覆盖 widget_class 类属性即可绑定对应的 DataWidget 类型。
不涉及按列号分发——每列使用独立的 Delegate 实例。

编辑期间透明背景处理：
  EditorLineEdit 设为 background: transparent，让表格行背景效果
  （交替行、悬浮、选中、明暗主题）自然透出。为避免底层单元格文字
  也透出，编辑期间 paint() 跳过文字绘制，只画背景。

Classes:
    DataWidgetDelegate: 单元格委托基类
"""

from typing import Any, cast

from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QColor, QFont, QPainter
from PySide6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem, QWidget
from qfluentwidgets import isDarkTheme

from gui.custom.views.base_view import BaseTableView
from gui.custom.widgets import DataWidget


def _font_from_dict(font_dict: dict) -> QFont | None:
    """将字体属性字典构造为 QFont

    支持的键：family, size, weight, italic。
    与 base_model._get_font 的构造逻辑保持一致。

    Args:
        font_dict: 字体属性字典

    Returns:
        QFont 实例，字典为空时返回 None
    """
    family = font_dict.get("family")
    if not family:
        return None
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


class DataWidgetDelegate(QStyledItemDelegate):
    """单元格委托基类

    子类通过覆盖 widget_class 指定编辑器类型：
        class MyDelegate(DataWidgetDelegate):
            widget_class = MyWidget

    createEditor / setEditorData / setModelData / updateEditorGeometry
    均已实现，子类一般无需重写。

    未设置 widget_class 的列将返回 None（只读）。
    """

    # 子类覆盖此属性指定 DataWidget 类型
    widget_class: type[DataWidget] | None = None

    def __init__(self, parent=None, font: QFont | dict | None = None):
        """初始化委托

        Args:
            parent: 父对象
            font: 编辑器字体，QFont 实例或字体属性字典，None 表示不设置
        """
        super().__init__(parent)
        self._font: QFont | None = None
        if isinstance(font, QFont):
            self._font = font
        elif isinstance(font, dict):
            self._font = _font_from_dict(font)

        # 正在编辑的单元格索引，用于 paint() 跳过文字绘制
        self._editing_index: QModelIndex | None = None

        # prototype 实例：不挂父节点、不显示，仅用作 format_display / parse_display
        self._prototype: DataWidget | None = None
        if self.widget_class is not None:
            self._prototype = self.widget_class()

    # ========== 绘制（委托给 View 默认的 TableItemDelegate） ==========

    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        """委托 TableItemDelegate 绘制背景/高亮/选中和文字

        编辑期间跳过文字绘制 — 编辑器设为透明背景以便表格行背景效果
        （交替行、悬浮、选中、明暗主题）自然透出，此处阻止底层文字也透出。
        """
        if self._editing_index is not None and index == self._editing_index:
            self._paint_background_only(painter, option, index)
            return

        view = cast(BaseTableView, self.parent())
        if view is not None and hasattr(view, "delegate") and view.delegate is not None:
            view.delegate.paint(painter, option, index)
        else:
            super().paint(painter, option, index)

    def _paint_background_only(
        self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex
    ) -> None:
        """只绘制单元格背景效果，不绘制文字

        镜像 qfluentwidgets TableItemDelegate.paint 的背景绘制部分
        （行高亮、交替色、选中指示器），但跳过末尾 super().paint()
        的文字绘制调用。编辑期间使用，配合透明编辑器避免底层文字透出。

        Args:
            painter: QPainter 实例
            option: 样式选项
            index: 单元格索引
        """
        view = cast(BaseTableView, self.parent())
        if view is None:
            super().paint(painter, option, index)
            return

        td = view.delegate  # TableItemDelegate 实例
        if td is None:
            super().paint(painter, option, index)
            return

        painter.save()
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setClipping(True)
        painter.setClipRect(option.rect)

        # 调整 margin，与 TableItemDelegate 一致
        option.rect.adjust(0, td.margin, 0, -td.margin)

        # ========== 行背景状态（镜像 TableItemDelegate.paint） ==========

        isHover = td.hoverRow == index.row()
        isPressed = td.pressedRow == index.row()
        isAlternate = index.row() % 2 == 0 and view.alternatingRowColors()
        isDark = isDarkTheme()

        c = 255 if isDark else 0
        alpha = 0

        if index.row() not in td.selectedRows:
            if isPressed:
                alpha = 9 if isDark else 6
            elif isHover:
                alpha = 12
            elif isAlternate:
                alpha = 5
        else:
            if isPressed:
                alpha = 15 if isDark else 9
            elif isHover:
                alpha = 25
            else:
                alpha = 17

        # ========== 背景填充 ==========

        bg = index.data(Qt.ItemDataRole.BackgroundRole)
        if bg is not None:
            painter.setBrush(bg)
        else:
            painter.setBrush(QColor(c, c, c, alpha))

        td._drawBackground(painter, option, index)

        # 首列选中指示器（与 TableItemDelegate 一致：仅首列且未水平滚动时绘制）
        if (
            index.row() in td.selectedRows
            and index.column() == 0
            and view.horizontalScrollBar().value() == 0
        ):
            td._drawIndicator(painter, option, index)

        painter.restore()
        # 不调用 super().paint() — 文字绘制在此跳过

    # ========== Delegate 接口 ==========

    def createEditor(self, parent: QWidget, option, index: QModelIndex) -> QWidget | None:
        """创建编辑器实例

        依据 widget_class 创建对应的 DataWidget。
        widget_class 为 None 时返回 None（只读列）。

        Args:
            parent: 编辑器父控件
            option: 样式选项
            index: 单元格索引

        Returns:
            DataWidget 实例或 None
        """
        if self.widget_class is None:
            return None
        editor = self.widget_class(parent)
        if self._font is not None:
            editor.apply_font(self._font)
        return editor

    def setEditorData(self, editor: QWidget, index: QModelIndex) -> None:
        """从 Model 读取数据填入编辑器

        Args:
            editor: createEditor 返回的 DataWidget 实例
            index: 单元格索引
        """
        if not isinstance(editor, DataWidget):
            return
        self._editing_index = index  # 标记编辑中，paint 跳过文字绘制
        value = index.data(self.getItemRole())
        editor.set_value(value)

    def setModelData(self, editor: QWidget, model, index: QModelIndex) -> None:
        """编辑器确认后将数据写回 Model

        Args:
            editor: DataWidget 实例
            model: 表格 Model
            index: 单元格索引
        """
        if not isinstance(editor, DataWidget):
            return
        value = editor.get_value()
        model.setData(index, value, self.setItemRole())
        self._editing_index = None  # 编辑结束，恢复文字绘制

    def destroyEditor(self, editor: QWidget, index: QModelIndex) -> None:
        """编辑器销毁时清除编辑标记

        Args:
            editor: DataWidget 实例
            index: 单元格索引
        """
        self._editing_index = None  # 编辑取消/关闭，恢复文字绘制
        super().destroyEditor(editor, index)

    def updateEditorGeometry(self, editor: QWidget, option, index: QModelIndex) -> None:
        """将编辑器位置设为单元格区域，上下各缩 1px 并锁定高度

        Args:
            editor: DataWidget 实例
            option: 样式选项
            index: 单元格索引
        """
        rect = option.rect.adjusted(3, 2, 0, -2)
        editor.setGeometry(rect)
        editor.setFixedHeight(rect.height())

    # ========== 格式化代理（委托给 prototype） ==========

    def format_display(self, value) -> str:
        """代理 prototype.format_display，供表格 DisplayRole 使用"""
        if self._prototype is None:
            return str(value)
        return self._prototype.format_display(value)

    def parse_display(self, text: str) -> Any:
        """代理 prototype.parse_display，供批量粘贴使用"""
        if self._prototype is None:
            raise NotImplementedError("no prototype")
        return self._prototype.parse_display(text)

    # ========== 角色扩展点 ==========

    def getItemRole(self) -> int:
        """读取数据时使用的角色

        Returns:
            Qt.ItemDataRole，默认 EditRole
        """
        return Qt.ItemDataRole.EditRole

    def setItemRole(self) -> int:
        """写回数据时使用的角色

        Returns:
            Qt.ItemDataRole，默认 EditRole
        """
        return Qt.ItemDataRole.EditRole
