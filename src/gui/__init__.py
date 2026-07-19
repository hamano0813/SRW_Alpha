"""
GUI 顶层包

聚合所有顶层界面框架的导入入口。

Classes:
    HomeFrame: 概览框架 - ROM 编辑器首页
    OptionFrame: 选项设置框架
    PilotFrame: 驾驶员编辑框架
    RobotFrame: 机器人编辑器框架
    SnmsgFrame: 消息编辑框架
    SndataFrame: 场景数据编辑框架
    ScriptFrame: 剧本编辑框架
    DictionaryFrame: 图鉴编辑框架
"""

from .dictionary.dictionary_frame import DictionaryFrame
from .home.home_frame import HomeFrame
from .option.option_frame import OptionFrame
from .pilot.pilot_frame import PilotFrame
from .robot.robot_frame import RobotFrame
from .script.script_frame import ScriptFrame
from .sndata.sndata_frame import SndataFrame
from .snmsg.snmsg_frame import SnmsgFrame
