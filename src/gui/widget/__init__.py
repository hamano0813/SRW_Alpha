"""
自定义控件包 - 统一导出入口

聚合表格体系、通用控件、代理框体和专用控件。
外部统一通过 from gui.widget import Xxx 引用。

Subpackages:
    table:   表格体系（模型、视图、委托、表格内编辑器）
    common:  通用面板控件（纯信号槽，供卡片层编排）
    proxy:   数据代理框体（ProxyFrame / CardHeader）
    special: 专用编辑器控件（特定数据类型的定制控件）
"""

from .abstract import VerticalSpinBox
from .common import (
    CommonBitCombo,
    CommonBitList,
    CommonMappingCombo,
    CommonMappingSpin,
    CommonNumberSpin,
    CommonStretchLabel,
)
from .proxy import CardHeader, ProxyFrame
from .special import (
    LevelSpin,
    RangeCombo,
    RobotCombo,
    SpiritCombo,
    SpiritsEditor,
)
from .table import (
    BaseTableModel,
    BaseTableView,
    CellEditor,
    CellMappingStepper,
    CellMultiLine,
    CellNumberStepper,
    CellSingleLine,
    DataWidgetDelegate,
    FixedTableModel,
    FixedTableView,
    MappingSpinDelegate,
    MultiLineDelegate,
    MutableTableModel,
    NumberSpinDelegate,
    SingleLineDelegate,
)
