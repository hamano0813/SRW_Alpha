"""
概览框架模块

提供 ROM 编辑器的首页界面，包含加载/保存 ROM 按钮和编辑项目表格。
"""

import os
import shutil

from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout
from qfluentwidgets import MessageBox, PrimaryPushButton, ScrollArea

import config

from .file_table import FileTable
from .progress_dialog import ProgressDialog

# 外部工具路径常量
DUMPSXISO = os.path.join(config.current_path, "tools", "dumpsxiso.exe")
MKPSXISO = os.path.join(config.current_path, "tools", "mkpsxiso.exe")


class HomeFrame(QFrame):
    """概览框架 - ROM 编辑器首页"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("EditorFrame")

        # 子框架容器，用于滚动
        self.sub_frame = QFrame()

        # ========== Load / Save 按钮（右对齐） ==========
        self.load_button = PrimaryPushButton(self.tr("Load ROM"), self)
        self.save_button = PrimaryPushButton(self.tr("Save ROM"), self)
        self.load_button.setFixedSize(180, 40)
        self.save_button.setFixedSize(180, 40)

        self.load_button.clicked.connect(self._on_load_rom)
        self.save_button.clicked.connect(self._on_save_rom)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)
        btn_layout.addStretch()
        btn_layout.addWidget(self.load_button)
        btn_layout.addWidget(self.save_button)

        # ========== 编辑项目表格 ==========
        self.table = FileTable(self)

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

    # ---- Cache 路径辅助 ----

    def _cache_paths(self) -> tuple[str, str]:
        """
        从配置获取缓存目录和对应的 XML 项目文件路径。

        Returns:
            (cache_path, xml_path)
        """
        cache_name = config.option.cache_dir.value
        cache_path = os.path.join(config.current_path, cache_name)
        xml_path = os.path.join(
            os.path.dirname(cache_path),
            os.path.basename(cache_path) + ".xml",
        )
        return cache_path, xml_path

    # ---- Load ROM ----

    def _on_load_rom(self):
        """加载 ROM —— 调用 dumpsxiso 解包到缓存目录"""
        rom_path = config.option.load_path.value
        if not rom_path:
            w = MessageBox(
                self.tr("ROM Path Not Configured"),
                self.tr("Please configure the ROM file path in Settings first."),
                self.window(),
            )
            w.exec()
            return

        if not os.path.isfile(rom_path):
            w = MessageBox(
                self.tr("File Not Found"),
                self.tr("ROM file does not exist:\n{}").format(rom_path),
                self.window(),
            )
            w.yesButton.setText(self.tr("OK"))
            w.cancelButton.hide()
            w.exec()
            return

        cache_path, xml_path = self._cache_paths()
        os.makedirs(cache_path, exist_ok=True)

        dialog = ProgressDialog(self.window())
        dialog.start(DUMPSXISO, ["-x", cache_path, "-s", xml_path, rom_path])
        if dialog.exec():
            # TODO: 加载完成后刷新表格等操作
            pass

    # ---- Save ROM ----

    def _on_save_rom(self):
        """保存 ROM —— 调用 mkpsxiso 从缓存目录重建镜像"""
        save_path = config.option.save_path.value
        if not save_path:
            w = MessageBox(
                self.tr("Save Path Not Configured"),
                self.tr("Please configure the ROM save path in Settings first."),
                self.window(),
            )
            w.exec()
            return

        cache_path, xml_path = self._cache_paths()
        if not os.path.isfile(xml_path):
            w = MessageBox(
                self.tr("File Not Found"),
                self.tr("Cache project file not found. Please load a ROM first."),
                self.window(),
            )
            w.yesButton.setText(self.tr("OK"))
            w.cancelButton.hide()
            w.exec()
            return

        # 从 .bin 路径推导对应的 .cue 路径
        output_bin = save_path
        output_cue = os.path.splitext(output_bin)[0] + ".cue"

        # 检查输出文件是否已存在
        if os.path.exists(output_bin):
            w = MessageBox(
                self.tr("File Already Exists"),
                self.tr("The output file already exists:\n{}\n\nDo you want to overwrite it?").format(output_bin),
                self.window(),
            )
            w.yesButton.setText(self.tr("Yes"))
            w.cancelButton.setText(self.tr("No"))
            if not w.exec():
                return

        dialog = ProgressDialog(self.window())
        dialog.start(MKPSXISO, ["-y", "-o", output_bin, "-c", output_cue, xml_path])
        if dialog.exec():
            os.startfile(os.path.dirname(output_bin))
            if config.option.auto_clean.value and os.path.isdir(cache_path):
                shutil.rmtree(cache_path, ignore_errors=True)

    # ---- i18n / Reset ----

    def translateUI(self):
        """更新界面文本翻译"""
        self.load_button.setText(self.tr("Load ROM"))
        self.save_button.setText(self.tr("Save ROM"))
        self.table.translateUI()

    def resetUI(self):
        """重置界面字体"""
        pass
