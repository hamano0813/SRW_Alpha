"""
special 专用编辑器控件子包

针对特定数据类型预配置的面板编辑器控件。
内部已绑定观察者模式，自动响应 ROM 数据变更。

Classes:
    RobotComboBox: 机体选择下拉框（自动同步 robots 索引）
"""

from .robot_combobox import RobotComboBox

__all__ = [
    "RobotComboBox",
]
