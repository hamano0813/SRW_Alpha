"""
界面框架子包 - 各编辑模块的顶层容器

聚合所有顶层界面框架，每个子包对应一个编辑模块。
各 Frame 从本包统一导出，供上层 gui 包直接 import。

Subpackages:
    home:       概览框架 - ROM 编辑器首页
    option:     选项设置框架
    pilot:      驾驶员编辑框架
    robot:      机体编辑框架
    script:     幕间编辑框架（待实现）
    sndata:     场景数据编辑框架（待实现）
    snmsg:      消息编辑框架
    dictionary: 图鉴编辑框架（待实现）

Classes:
    DictionaryFrame: 图鉴编辑框架
    HomeFrame:       概览框架 - ROM 编辑器首页
    OptionFrame:     选项设置框架
    PilotFrame:      驾驶员编辑框架
    UnitFrame:       机体编辑框架
    ScriptFrame:     幕间编辑框架
    SndataFrame:     场景数据编辑框架
    SnmsgFrame:      消息编辑框架
"""

from .dictionary.dictionary_frame import DictionaryFrame
from .home.home_frame import HomeFrame
from .option.option_frame import OptionFrame
from .pilot.pilot_frame import PilotFrame
from .unit.unit_frame import UnitFrame
from .script.script_frame import ScriptFrame
from .sndata.sndata_frame import SndataFrame
from .snmsg.snmsg_frame import SnmsgFrame
