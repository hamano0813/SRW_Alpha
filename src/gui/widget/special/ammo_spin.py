"""
弹药微调框 - CommonNumberSpin 的特化版本

内嵌 VerticalSpinBox，常用于武器弹数编辑。
双字段写回逻辑已移至卡片层处理。

Classes:
    AmmoSpin: 弹药微调框
"""

from gui.widget.common import CommonNumberSpin


class AmmoSpin(CommonNumberSpin):
    """弹药微调框 - CommonNumberSpin 的特化子类，预设弹药范围"""

    def __init__(self, value_range: tuple[int, int] | None = None, parent=None):
        """初始化弹药微调框

        Args:
            value_range: (最小值, 最大值)
            parent: 父 QWidget
        """
        super().__init__(value_range, parent=parent)
