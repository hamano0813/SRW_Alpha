"""
通用面板控件 - 信号槽收发，供卡片层编排

所有控件继承 PanelEditor，通过 set_model/set_row 读写数据。
PanelEditor 负责持有 model 引用并按 field 键读写。
VerticalSpinBox 和 StretchLabel 为辅助组件。

Classes:
    PanelEditor / BitCheckList / BitComboBox / MappingComboBox /
    MappingCompSpin / NumberCompSpin / VerticalSpinBox / StretchLabel
"""

from .bit_checklist import BitCheckList
from .bit_combobox import BitComboBox
from .mapping_combobox import MappingComboBox
from .mapping_compspin import MappingCompSpin
from .number_compspin import NumberCompSpin
from .panel_editor import PanelEditor
from .spin_box import VerticalSpinBox
from .stretch_label import StretchLabel
