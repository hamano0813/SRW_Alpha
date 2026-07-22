"""
机体选择下拉框 - 绑定 robots 观察者，自动同步选项

继承 MappingCombo，自动注册为 Rom.robots 的观察者。
当机体数据变更时，下拉选项自动同步刷新。

Classes:
    RobotCombo: 机体选择下拉框
"""

from typing import Any

from gui.custom.fonts import JP_FONT, JP_QFONT
from gui.widget.common import MappingCombo


class RobotCombo(MappingCombo):
    """机体选择下拉框 - 自动同步 robots 索引

    通过 self.window().rom 获取 Rom 实例并注册为 robots 观察者。
    选项变更时自动刷新，选中项保持不变。
    额外扩展键值对通过 supplements 参数传入（如特殊驾驶员等非 ROM 数据）。
    """

    def __init__(self, parent=None, supplements: dict[int, str] | None = None):
        """初始化机体选择下拉框

        Args:
            parent:      父 QWidget
            supplements: 额外键值对，通过 robots | supplements 合并到选项中
        """
        super().__init__(parent=parent)
        self.apply_font(JP_FONT)
        self.set_dropdown_font(JP_QFONT)
        self._supplements = supplements or {}
        self._cb = self._on_robots_changed
        self._registered: bool = False

    # ========== 观察者注册 ==========

    def register(self) -> None:
        """尝试注册 robots 观察者（幂等），数据就绪后由 notify 推送

        由卡片在模型就绪后调用。
        """
        if self._registered:
            return
        mw = self.window()
        if mw and hasattr(mw, "rom"):
            mw.rom.observe("robots", self._cb, supplements=self._supplements)  # type: ignore
            self._registered = True

    # ========== 观察者回调 ==========

    def _on_robots_changed(self, robots: dict[int, str]) -> None:
        """机体数据变更时刷新下拉选项，保持当前选中值"""
        self.set_mapping(robots)
