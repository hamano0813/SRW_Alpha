"""
AmmoSpin 弹药微调框 - 同时修改 ammod 和 ammom

内嵌 VerticalSpinBox，修改时同步更新"初期弾数"和"最大弾数"两个字段。

放置于 widgets/special/ 子包。

Classes:
    AmmoSpin: 弹药微调框
"""

from gui.custom.widgets.panel.number_compspin import NumberCompSpin


class AmmoSpin(NumberCompSpin):
    """弹药微调框 - 显示 ammom，修改时同步写入 ammod 和 ammom"""

    def __init__(self, value_range: tuple[int, int] | None = None, parent=None):
        """初始化弹药微调框

        Args:
            value_range: (最小值, 最大值)
            parent: 父 QWidget
        """
        # 两个字段名写死在此
        self._field_a = "ammod"  # 初期弾数
        self._field_b = "ammom"  # 最大弾数

        # 以 ammom 作为主字段传给 NumberCompSpin
        super().__init__(self._field_b, value_range, parent=parent)

    # ========== 覆盖：写回时同步两个字段 ==========

    def _on_value_changed(self, value: int) -> None:
        """值改变时同步 _value 并写回字典（两个字段一起写）"""
        self._value = value
        if self._model is not None and self._row >= 0:
            row_data = self._model.get_row_data(self._row)
            row_data[self._field_a] = value
            row_data[self._field_b] = value
        self.dataChanged.emit(self._field_b)
