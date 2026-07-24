"""
数值微调框 - 在指定范围内步进

直接继承 VerticalSpinBox，无 QWidget 壳。
使用 FluentIcon 箭头直接步进，无 flyout。

Classes:
    CommonNumberSpin: 数值微调框
"""

from PySide6.QtGui import QFont

from gui.widget.abstract import VerticalSpinBox


class CommonNumberSpin(VerticalSpinBox):
    """数值微调框 - 在 [min, max] 范围内步进

    直接继承 VerticalSpinBox，编辑后发射 valueChanged(int)，
    外部通过 set_value 控制显示。
    """

    def __init__(self, value_range: tuple[int, int] | None = None,
                 show_sign: bool = False, editable: bool = True, parent=None):
        """初始化数值微调框

        Args:
            value_range: (最小值, 最大值)，None 默认 (0, 9999)
            show_sign:   是否强制显示正号
            editable:    是否允许键盘输入
            parent:      父 QWidget
        """
        super().__init__(parent, editable=editable)

        min_val, max_val = value_range or (0, 9999)
        self._show_sign = show_sign

        self.setRange(min_val, max_val)

    # ========== 数据接口 ==========

    def set_value(self, value: int) -> None:
        """设置当前值并刷新显示"""
        self.blockSignals(True)
        self.setValue(int(value))
        self.blockSignals(False)

    def value(self) -> int:
        """获取当前值"""
        return super().value()

    # ========== 取值范围 ==========

    def set_range(self, min_val: int, max_val: int) -> None:
        """更新取值范围"""
        self.setRange(min_val, max_val)

    # ========== 显示格式 ==========

    def textFromValue(self, value: int) -> str:
        """数值 → 显示文本，show_sign 时正值显示 +N"""
        if self._show_sign and value >= 0:
            return f"+{value}"
        return str(value)

    # ========== 字体 ==========

    def apply_font(self, font: QFont | dict) -> None:
        """设置编辑器字体"""
        if isinstance(font, dict):
            qfont = QFont()
            family = font.get("family")
            size = font.get("size")
            weight = font.get("weight")
            italic = font.get("italic")
            if family:
                qfont.setFamily(family)
            if size:
                qfont.setPixelSize(size)
            if weight:
                qfont.setWeight(weight)
            if italic:
                qfont.setItalic(italic)
            font = qfont
        self.setFont(font)

    def resetUI(self) -> None:
        """从全局配置刷新字体"""
        super().resetUI()
