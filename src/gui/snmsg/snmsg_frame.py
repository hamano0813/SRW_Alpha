"""
消息编辑框架模块

提供消息数据的表格展示和编辑界面，配合 MESSAGE 解析模块使用。
左表右面板布局，右侧 MsgPanel 提供搜索过滤、行号跳转和说话人过滤功能。

Classes:
    SnmsgFrame: 消息编辑框架
"""

from collections import Counter

from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtWidgets import QHBoxLayout, QWidget

from gui.custom.widgets.proxy_frame import ProxyFrame
from gui.snmsg.msg_frame import MsgFrame
from gui.snmsg.msg_panel import MsgPanel


def _extract_speakers(data: list[dict]) -> list[str]:
    """从消息数据中提取说话人列表（按出现次数降序）

    Args:
        data: [{"snmsg": str}, ...]

    Returns:
        说话人名列表
    """
    counter = Counter()
    for item in data:
        text = item["snmsg"]
        first_line = text.split("\n")[0]
        if "「" in first_line:
            idx = first_line.index("「")
            if idx > 0:
                name = first_line[:idx].strip()
                counter[name] += 1
    return [name for name, _ in counter.most_common()]


class SnmsgFrame(ProxyFrame):
    """消息编辑框架 - 左表右面板布局"""

    def __init__(self, fields, parent=None):
        """初始化消息编辑框架

        Args:
            fields: FieldMapping 字段映射实例
            parent: 父 QWidget
        """
        super().__init__(parent)
        self.setObjectName("MessageFrame")

        self._rom_data: dict | None = None
        self._mutex_guard: bool = False  # 互斥递归防护

        # ========== 消息主表 ==========

        self._msg_frame = MsgFrame()
        self._msg_frame.set_field(fields)
        # ========== 配置代理模型过滤 ==========

        self._msg_frame.message_view.proxy_model().setFilterKeyColumn(0)
        self._msg_frame.message_view.proxy_model().setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._msg_frame.message_view.source_model().dataChanged.connect(self._on_data_changed)

        # ========== 右侧面板 ==========

        self._panel = MsgPanel(self)
        self._panel.filterChanged.connect(self._on_filter_changed)
        self._panel.filterCleared.connect(lambda: self._on_filter_changed(""))
        self._panel.gotoRequested.connect(self._on_goto)
        self._panel.speakerChanged.connect(self._on_speaker_filter)

        # ========== 布局 ==========

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._msg_frame)
        layout.addWidget(self._panel)

        self.setLayout(layout)

    # ========== 焦点策略 ==========

    def showEvent(self, event):
        """每次显示时把焦点交给表格，右侧面板输入框不抢焦点"""
        super().showEvent(event)
        self._msg_frame.message_view.setFocus()

    # ========== 搜索过滤（互斥） ==========

    def _on_filter_changed(self, text: str) -> None:
        """按文本过滤表格行，同时清空说话人和跳转

        Args:
            text: 过滤关键词
        """
        if self._mutex_guard:
            return
        self._mutex_guard = True
        self._panel.clear_speaker()
        self._panel.clear_goto()
        self._mutex_guard = False
        self._msg_frame.message_view.proxy_model().setFilterFixedString(text)

    def _on_goto(self, row: int) -> None:
        """跳转到十六进制行号指定的源行，同时清空文本过滤和说话人

        Args:
            row: 源模型行号
        """
        if self._mutex_guard:
            return
        self._mutex_guard = True
        self._panel.clear_filter()
        self._panel.clear_speaker()
        # 清理其他过滤（guard 阻止了对应的信号槽，需手动清除）
        self._msg_frame.message_view.proxy_model().setFilterFixedString("")
        self._mutex_guard = False
        self._msg_frame.message_view.select_source_row(row)

    def _on_speaker_filter(self, text: str) -> None:
        """按说话人过滤表格行，同时清空文本过滤和跳转

        Args:
            text: 选中的说话人名，空文本清除过滤
        """
        if self._mutex_guard:
            return
        self._mutex_guard = True
        self._panel.clear_filter()
        self._panel.clear_goto()
        self._mutex_guard = False
        text = text.strip()
        if not text:
            self._msg_frame.message_view.proxy_model().setFilterFixedString("")
        else:
            pattern = QRegularExpression.escape(text) + "「"
            self._msg_frame.message_view.proxy_model().setFilterRegularExpression(pattern)

    def _on_data_changed(self):
        """表格数据编辑后重新提取说话人列表"""
        data = self._msg_frame.message_view.source_model().get_data()
        self._panel.set_speakers(_extract_speakers(data))

    # ========== 数据解析 ==========

    def set_rom_data(self, data: dict) -> None:
        """装入 ROM 的消息数据

        取 snmsgs 消息列表填入主表格，并初始化说话人列表。

        Args:
            data: Rom().parse_messages() 返回的 dict
        """
        self._rom_data = data
        snmsgs_data = data.get("snmsgs", {})
        snmsgs_list = snmsgs_data.get("snmsgs", [])

        self._msg_frame.set_data(snmsgs_list)
        self._panel.set_speakers(_extract_speakers(snmsgs_list))
