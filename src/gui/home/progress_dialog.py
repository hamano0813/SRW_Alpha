"""
ROM 操作进度对话框

使用 QProcess 异步执行 dumpsxiso / mkpsxiso，
在对话框中实时显示工具的标准输出/错误日志。
"""

from PySide6.QtCore import QProcess, Qt
from PySide6.QtWidgets import QDialog, QVBoxLayout
from qfluentwidgets import PrimaryPushButton, TextEdit, isDarkTheme


class ProgressDialog(QDialog):
    """显示 ROM 工具执行日志的进度对话框"""

    def __init__(self, parent=None):
        super().__init__(parent, f=Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(680, 400)

        # 日志文本框
        self._log = TextEdit(self)
        self._log.setReadOnly(True)
        self._log.setMinimumHeight(200)

        # 关闭按钮（进程结束后启用）
        self._button = PrimaryPushButton(self.tr("Close"))
        self._button.setEnabled(False)
        self._button.setFixedHeight(40)

        self._buffer = ""  # 用于合并 \r 跨块到达的输出

        layout = QVBoxLayout()
        layout.addWidget(self._log)
        layout.addWidget(self._button)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        self.setLayout(layout)

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
        """将进程输出追加到日志文本框，合并 \r 跨块数据"""
        self._buffer += self._process.readAllStandardOutput().data().decode("utf-8", errors="replace")  # type: ignore
        self._buffer = self._buffer.replace("\r", "")  # \r -> 直接删除，视为同一行

        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            self._log.append(line.rstrip())

        scrollbar = self._log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def resetUI(self):
        """根据当前主题设置对话框背景色"""
        if isDarkTheme():
            self.setStyleSheet("""QDialog{background:#292929;}""")
        else:
            self.setStyleSheet("""QDialog{background:white;}""")

    def showEvent(self, a0):
        self.resetUI()
