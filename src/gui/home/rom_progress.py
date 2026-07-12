"""
ROM 操作进度对话框

使用 QProcess 异步执行 dumpsxiso / mkpsxiso，
在 Fluent 对话框中实时显示工具的标准输出/错误日志。
"""

from PySide6.QtCore import QProcess, Qt, Signal
from PySide6.QtWidgets import QDialog, QVBoxLayout
from qfluentwidgets import Dialog, PrimaryPushButton, TextEdit, isDarkTheme


class RomProgressDialog(QDialog):
    """显示 ROM 工具执行日志的 Fluent 进度对话框"""

    finished = Signal(int)  # 进程退出码

    def __init__(self, parent=None):
        super().__init__(parent, f=Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(680, 400)

        # 日志文本框（放到 textLayout 中标签之间）
        self._log = TextEdit(self)
        self._log.setReadOnly(True)
        self._log.setLineWrapMode(TextEdit.LineWrapMode.NoWrap)
        self._log.setMinimumHeight(200)

        self._button = PrimaryPushButton(self.tr("Close"))
        self._button.setEnabled(False)
        self._button.setFixedHeight(40)

        layout = QVBoxLayout()
        layout.addWidget(self._log)
        layout.addWidget(self._button)
        self.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # QProcess 异步进程
        self._process = QProcess(self)
        self._process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self._process.readyReadStandardOutput.connect(self._on_output)
        self._process.finished.connect(lambda: self._button.setEnabled(True))

        self._button.clicked.connect(self.accept)

    def start(self, program: str, args: list[str]) -> None:
        """启动外部进程并捕获输出"""
        self._log.clear()
        self._process.start(program, args)

    def _on_output(self):
        """将进程输出追加到日志文本框"""
        text = self._process.readAllStandardOutput().data().decode("utf-8", errors="replace")  # type: ignore
        self._log.append(text.rstrip())
        scrollbar = self._log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def resetUI(self):
        if isDarkTheme():
            self.setStyleSheet("""QDialog{background:#292929;}""")
        else:
            self.setStyleSheet("""QDialog{background:white;}""")

    def showEvent(self, a0):
        self.resetUI()
