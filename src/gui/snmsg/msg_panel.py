"""
消息侧边栏面板 - 搜索过滤与行号跳转

两个 HeaderCardWidget 垂直排列，分别提供文字过滤和十六进制行号跳转功能。
通过自定义信号与上级界面通信。

Classes:
    MsgPanel: 消息侧边栏面板
"""

from PySide6.QtCore import QRegularExpression, Qt, Signal
from PySide6.QtGui import QRegularExpressionValidator, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QVBoxLayout
from qfluentwidgets import (
    BodyLabel,
    EditableModelComboBox,
    HeaderCardWidget,
    SearchLineEdit,
)

from gui.custom.proxy_frame import ProxyFrame


class _FilterCard(HeaderCardWidget):
    """搜索过滤卡片 - 点击搜索按钮过滤表格"""

    filterChanged = Signal(str)  # 过滤文字
    filterCleared = Signal()  # 清除过滤

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Search"))

        self.viewLayout.setContentsMargins(20, 16, 20, 16)

        self._info_label = BodyLabel(self.tr("Enter text to filter messages"), self)
        self._filter_edit = SearchLineEdit(self)
        self._filter_edit.setPlaceholderText(self.tr("filter..."))
        self._filter_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self._filter_edit.searchSignal.connect(self.filterChanged)
        self._filter_edit.clearSignal.connect(self.filterCleared)
        self._filter_edit.returnPressed.connect(lambda: self.filterChanged.emit(self._filter_edit.text()))

        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._info_label)
        layout.addWidget(self._filter_edit)

        self.viewLayout.addLayout(layout)

    def mousePressEvent(self, e):
        """点击卡片空白区域取消子控件焦点"""
        self.setFocus()
        super().mousePressEvent(e)

    def translateUI(self):
        """刷新卡片标题和提示文本"""
        self.setTitle(self.tr("Search"))
        self._info_label.setText(self.tr("Enter text to filter messages"))
        self._filter_edit.setPlaceholderText(self.tr("filter..."))


class _GotoCard(HeaderCardWidget):
    """行号跳转卡片 - 点击搜索按钮跳转到指定行"""

    gotoRequested = Signal(int)  # 源行号
    gotoCleared = Signal()  # 清除输入

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Go to"))

        self.viewLayout.setContentsMargins(20, 16, 20, 16)

        self._info_label = BodyLabel(self.tr("Enter hex row number to locate"), self)
        self._goto_edit = SearchLineEdit(self)
        self._goto_edit.setPlaceholderText(self.tr("hex row..."))
        self._goto_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self._goto_edit.setValidator(QRegularExpressionValidator(QRegularExpression("[0-9A-Fa-f]*"), self._goto_edit))
        self._goto_edit.searchSignal.connect(self._on_search)
        self._goto_edit.clearSignal.connect(self.gotoCleared)
        self._goto_edit.returnPressed.connect(lambda: self._on_search(self._goto_edit.text()))
        self._goto_edit.textChanged.connect(self._on_text_changed)

        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._info_label)
        layout.addWidget(self._goto_edit)

        self.viewLayout.addLayout(layout)

    def mousePressEvent(self, e):
        """点击卡片空白区域取消子控件焦点"""
        self.setFocus()
        super().mousePressEvent(e)

    def _on_text_changed(self, text: str):
        """输入时过滤非法字符并自动转大写

        Args:
            text: 当前文本
        """
        upper = text.upper()
        if upper != text:
            self._goto_edit.blockSignals(True)
            self._goto_edit.setText(upper)
            self._goto_edit.blockSignals(False)

    def _on_search(self, text: str):
        """点击搜索按钮时解析十六进制文本并发射信号

        Args:
            text: 输入文本
        """
        text = text.strip()
        if not text:
            self.gotoCleared.emit()
            return
        try:
            row = int(text, 16)
        except ValueError:
            return
        self.gotoRequested.emit(row)

    def translateUI(self):
        """刷新卡片标题和提示文本"""
        self.setTitle(self.tr("Go to"))
        self._info_label.setText(self.tr("Enter hex row number to locate"))
        self._goto_edit.setPlaceholderText(self.tr("hex row..."))


class _SpeakerCard(HeaderCardWidget):
    """说话人过滤卡片 - 下拉选择说话人过滤表格"""

    speakerChanged = Signal(str)  # 选中的说话人名，空文本清除过滤

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Speaker"))

        self.viewLayout.setContentsMargins(20, 16, 20, 16)

        self._info_label = BodyLabel(self.tr("Select a speaker to filter messages"), self)
        self._speaker_combo = EditableModelComboBox(self)
        self._speaker_combo.setPlaceholderText(self.tr("all speakers"))
        self._speaker_combo.setClearButtonEnabled(True)
        self._speaker_combo.setMaxVisibleItems(10)
        self._speaker_combo.setReadOnly(True)
        self._speaker_combo.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self._speaker_combo.currentTextChanged.connect(self.speakerChanged)

        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._info_label)
        layout.addWidget(self._speaker_combo)

        self.viewLayout.addLayout(layout)

    def mousePressEvent(self, e):
        """点击卡片空白区域取消子控件焦点"""
        self.setFocus()
        super().mousePressEvent(e)

    def set_speakers(self, speakers: list[str]) -> None:
        """设置说话人下拉列表

        Args:
            speakers: 说话人名列表（按出现次数降序）
        """
        current = self._speaker_combo.text()
        self._speaker_combo.blockSignals(True)
        model = QStandardItemModel()
        for name in speakers:
            model.appendRow(QStandardItem(name))
        self._speaker_combo.setModel(model)
        self._speaker_combo.setCurrentIndex(-1)
        if current and self._speaker_combo.findText(current) >= 0:
            self._speaker_combo.setText(current)
        self._speaker_combo.blockSignals(False)
        # 同步最终状态（清空或维持选中），确保过滤条件与界面一致
        self.speakerChanged.emit(self._speaker_combo.text())

    def translateUI(self):
        """刷新卡片标题和提示文本"""
        self.setTitle(self.tr("Speaker"))
        self._info_label.setText(self.tr("Select a speaker to filter messages"))
        self._speaker_combo.setPlaceholderText(self.tr("all speakers"))


class MsgPanel(ProxyFrame):
    """消息侧边栏面板 - 搜索过滤 + 行号跳转 + 说话人过滤"""

    filterChanged = Signal(str)
    filterCleared = Signal()
    gotoRequested = Signal(int)
    gotoCleared = Signal()
    speakerChanged = Signal(str)

    def __init__(self, parent=None):
        """初始化消息侧边栏面板

        Args:
            parent: 父 QWidget
        """
        super().__init__(parent)

        self._filter_card = _FilterCard(self)
        self._goto_card = _GotoCard(self)
        self._speaker_card = _SpeakerCard(self)

        # 中转信号
        self._filter_card.filterChanged.connect(self.filterChanged)
        self._filter_card.filterCleared.connect(self.filterCleared)
        self._goto_card.gotoRequested.connect(self.gotoRequested)
        self._goto_card.gotoCleared.connect(self.gotoCleared)
        self._speaker_card.speakerChanged.connect(self.speakerChanged)

        # ========== 面板尺寸 ==========

        self.setMinimumWidth(260)
        self.setMaximumWidth(400)

        # ========== 布局 ==========

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addWidget(self._filter_card)
        layout.addWidget(self._goto_card)
        layout.addWidget(self._speaker_card)
        layout.addStretch()

        self.setLayout(layout)

    def mousePressEvent(self, e):
        """点击面板空白区域取消子控件焦点"""
        focused = self.focusWidget()
        if focused:
            focused.clearFocus()
        super().mousePressEvent(e)

    def set_speakers(self, speakers: list[str]) -> None:
        """设置说话人下拉列表

        Args:
            speakers: 说话人名列表
        """
        self._speaker_card.set_speakers(speakers)

    def clear_filter(self) -> None:
        """清空过滤文本"""
        self._filter_card._filter_edit.clear()

    def clear_speaker(self) -> None:
        """清空说话人选择"""
        self._speaker_card._speaker_combo.setCurrentIndex(-1)

    def clear_goto(self) -> None:
        """清空跳转输入"""
        self._goto_card._goto_edit.clear()
