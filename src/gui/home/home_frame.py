"""
主页框架模块

提供ROM编辑器的首页界面，包含加载/保存ROM按钮和编辑项目表格。
"""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout
from qfluentwidgets import PrimaryPushButton, ScrollArea

from .file_table import RequireFileTable


class HomeFrame(QFrame):
    """主页框架 - ROM编辑器首页"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("EditorFrame")

        # 创建子框架容器
        self.sub_frame = QFrame()

        # ========== Load / Save 按钮（右对齐） ==========
        self.load_button = PrimaryPushButton(self.tr("Load ROM"), self)
        self.save_button = PrimaryPushButton(self.tr("Save ROM"), self)
        self.load_button.setFixedSize(180, 40)
        self.save_button.setFixedSize(180, 40)

        # 注：按钮暂时没有连接槽函数

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)
        btn_layout.addStretch()
        btn_layout.addWidget(self.load_button)
        btn_layout.addWidget(self.save_button)

        # ========== 编辑项目表格 ==========
        self.table = RequireFileTable(self)

        # ========== 子框架布局 ==========
        sub_layout = QVBoxLayout()
        sub_layout.setSpacing(16)
        sub_layout.setContentsMargins(40, 20, 40, 20)
        sub_layout.addLayout(btn_layout)
        sub_layout.addWidget(self.table)
        self.sub_frame.setLayout(sub_layout)

        # ========== 滚动区域 ==========
        self.scroll_area = ScrollArea(self)
        self.scroll_area.setWidget(self.sub_frame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.enableTransparentBackground()

        # ========== 主布局 ==========
        layout = QVBoxLayout(self)
        layout.addWidget(self.scroll_area)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def translateUI(self):
        """更新界面文本翻译"""
        self.load_button.setText(self.tr("Load ROM"))
        self.save_button.setText(self.tr("Save ROM"))
        self.table.translateUI()

    def resetUI(self):
        """重置界面字体"""
        pass
