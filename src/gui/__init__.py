"""
GUI 顶层包

聚合所有顶层界面框架的导入入口。
使用 __getattr__ 延迟导入避免循环引用。

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

_FRAME_MODULES = {
    "DictionaryFrame": ".dictionary.dictionary_frame",
    "HomeFrame": ".home.home_frame",
    "OptionFrame": ".option.option_frame",
    "PilotFrame": ".pilot.pilot_frame",
    "RobotFrame": ".robot.robot_frame",
    "ScriptFrame": ".script.script_frame",
    "SndataFrame": ".sndata.sndata_frame",
    "SnmsgFrame": ".snmsg.snmsg_frame",
}


def __getattr__(name: str):
    """延迟导入各 Frame 类，避免模块加载时的循环依赖"""
    module = _FRAME_MODULES.get(name)
    if module is not None:
        import importlib

        cls = getattr(importlib.import_module(module, __package__), name)
        globals()[name] = cls
        return cls
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
