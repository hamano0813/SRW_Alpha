"""
单行文本编辑器 - DataWidget 子类

内嵌 FirstColLineEdit（首列专用自绘编辑器），完成表格内文本编辑。
后续可扩展子类切换不同的 LineEdit 实例以适应不同列。

Classes:
    LineTextWidget: 首列单行文本编辑器
"""

from typing import Any

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QSizePolicy, QVBoxLayout

from .data_widget import DataWidget
from .editor_lineedit import FirstColLineEdit


class LineTextWidget(DataWidget):
    """首列单行文本编辑器 — 文本即原始值

    内嵌 FirstColLineEdit（纯 QLineEdit 自绘，无 QSS 干扰），
    左圆右直，与表格首列视觉一致。
    """

    def __init__(self, parent=None):
        """初始化单行文本编辑器

        Args:
            parent: 父 QWidget
        """
        super().__init__(parent)

        # ========== 内嵌编辑器 ==========

        self._line_edit = FirstColLineEdit()
        self._line_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        # 微调文本位置 + 透明背景（背景由 delegate 层绘制，编辑器不额外遮挡）
        self._line_edit.setStyleSheet(
            "QLineEdit { padding-left: 14px; padding-top: 1px; padding-bottom: 1px; background: transparent; }"
        )

        # 将焦点代理给内部编辑器，双击编辑时立即获得输入光标
        self.setFocusProxy(self._line_edit)

        # ========== 信号 ==========

        self._line_edit.textChanged.connect(self._on_text_changed)

        # ========== 布局 ==========

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._line_edit)

    # ========== 数据读写 ==========

    def set_value(self, value) -> None:
        """存入文本值并刷新显示

        Args:
            value: 字符串文本
        """
        super().set_value(value)

    def get_value(self) -> str:
        """返回当前文本值"""
        return self._value if self._value is not None else ""

    # ========== 格式化 ==========

    def format_value(self) -> None:
        """将 _value 同步到编辑器显示，光标定位到末尾"""
        self._line_edit.blockSignals(True)
        self._line_edit.setText(str(self._value) if self._value is not None else "")
        self._line_edit.setCursorPosition(len(self._line_edit.text()))
        self._line_edit.blockSignals(False)

    # ========== 字体 ==========

    def apply_font(self, font: QFont) -> None:
        """将字体应用到内部编辑器

        Args:
            font: 要应用的 QFont
        """
        self._line_edit.setFont(font)

    # ========== 校验 ==========

    def validate(self, value) -> bool:
        """校验值是否为字符串类型"""
        return isinstance(value, str)

    # ========== 显示文本 ==========

    def format_display(self, value) -> str:
        """将值格式化为显示文本"""
        return str(value) if value is not None else ""

    # ========== 内部槽 ==========

    def _on_text_changed(self, text: str) -> None:
        """用户输入时同步 _value 并发射 dataChanged"""
        self._value = text
        self.dataChanged.emit(self._value)
