"""
概览框架模块

提供 ROM 编辑器的首页界面，包含解包/重建 ROM 按钮和 XML 项目树。
使用 dumpsxiso / mkpsxiso 工具进行 ROM 的解包和重建。

Classes:
    HomeFrame: 概览框架 - ROM 编辑器首页
"""

import os
import shutil

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout
from qfluentwidgets import (
    MessageBox,
    PrimaryPushButton,
    PushButton,
    ScrollArea,
    setFont,
)

import config

from .progress_dialog import ProgressDialog
from .xml_tree import XmlTreeView

DUMPSXISO = os.path.join(config.current_path, "tools", "dumpsxiso.exe")
MKPSXISO = os.path.join(config.current_path, "tools", "mkpsxiso.exe")


class HomeFrame(QFrame):
    """概览框架 - ROM 编辑器首页"""

    parseClicked = Signal()
    buildClicked = Signal()

    def __init__(self, parent=None):
        """初始化首页布局：按钮栏、XML 项目树和滚动区域"""
        super().__init__(parent)
        self.setObjectName("EditorFrame")

        self.sub_frame = QFrame()

        # 翻译关键字
        self._close_text = self.tr("Close")
        self._extract_rom_text = self.tr("Extract ROM")
        self._rebuild_rom_text = self.tr("Rebuild ROM")
        self._parse_cache_text = self.tr("Parse Cache")
        self._build_cache_text = self.tr("Build Cache")

        # MessageBox 翻译关键字
        self._msg_rom_path_not_set = self.tr("ROM Path Not Configured")
        self._msg_config_rom_path = self.tr("Please configure the ROM file path in Settings first.")
        self._msg_file_not_found = self.tr("File Not Found")
        self._msg_rom_not_exist = self.tr("ROM file does not exist:\n{}")
        self._msg_ok = self.tr("OK")
        self._msg_target_rom_not_set = self.tr("Target ROM Not Configured")
        self._msg_config_target_rom = self.tr("Please configure the target ROM path in Settings first.")
        self._msg_cache_not_found = self.tr("Cache project file not found. Please extract a ROM first.")
        self._msg_cache_dir_not_found = self.tr("Cache directory not found. Please extract a ROM first.")
        self._msg_cache_exists = self.tr("Cache already exists. Overwrite?")
        self._msg_cache_overwrite = self.tr("The cache directory already exists. Do you want to overwrite it?")
        self._msg_overwrite = self.tr("Overwrite")
        self._msg_cancel = self.tr("Cancel")
        self._msg_build_title = self.tr("Build Cache")
        self._msg_build_confirm = self.tr("Are you sure you want to build modified data to cache files?")
        self._msg_file_exists = self.tr("File Already Exists")
        self._msg_overwrite_prompt = self.tr("The output file already exists:\n{}\n\nDo you want to overwrite it?")
        self._msg_yes = self.tr("Yes")
        self._msg_no = self.tr("No")

        # 按钮区域（右对齐）
        self.extract_button = PushButton(self._extract_rom_text, self)
        self.rebuild_button = PushButton(self._rebuild_rom_text, self)
        self.parse_button = PrimaryPushButton(self._parse_cache_text, self)
        self.build_button = PrimaryPushButton(self._build_cache_text, self)
        self.extract_button.setFixedSize(180, 40)
        self.rebuild_button.setFixedSize(180, 40)
        self.parse_button.setFixedSize(180, 40)
        self.build_button.setFixedSize(180, 40)

        self.extract_button.clicked.connect(self._on_extract_rom)
        self.rebuild_button.clicked.connect(self._on_rebuild_rom)
        self.parse_button.clicked.connect(self._on_parse)
        self.build_button.clicked.connect(self._on_build)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)
        btn_layout.addStretch()
        btn_layout.addWidget(self.extract_button)
        btn_layout.addWidget(self.rebuild_button)
        btn_layout.addWidget(self.parse_button)
        btn_layout.addWidget(self.build_button)

        self._headers = [
            self.tr("File"),
            self.tr("Robot"),
            self.tr("Pilot"),
            self.tr("Message"),
            self.tr("Scenario"),
            self.tr("Intermission"),
            self.tr("Dictionary"),
        ]
        self._datas = {
            self.tr("Robot"): [
                "ROBOT.RAF",
            ],
            self.tr("Pilot"): [
                "PILOT.BIN",
            ],
            self.tr("Message"): ["SNMSG.BIN"],
            self.tr("Scenario"): [
                "ROBOT.RAF",
                "PILOT.BIN",
                "SNMSG.BIN",
                "SNDATA.BIN",
                "ENLIST.BIN",
                "AIUNP.BIN",
            ],
            self.tr("Intermission"): [
                "SCRIPT.BIN",
            ],
            self.tr("Dictionary"): ["DR.BIN", "DC.BIN"],
        }

        self.tree = XmlTreeView(self._headers, self._datas, self)

        sub_layout = QVBoxLayout()
        sub_layout.setSpacing(12)
        sub_layout.setContentsMargins(16, 12, 16, 12)
        sub_layout.addLayout(btn_layout)
        sub_layout.addWidget(self.tree)
        self.sub_frame.setLayout(sub_layout)

        self.scroll_area = ScrollArea(self)
        self.scroll_area.setWidget(self.sub_frame)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.enableTransparentBackground()

        layout = QVBoxLayout(self)
        layout.addWidget(self.scroll_area)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    # ========== 缓存路径辅助 ==========

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

    # ========== 解包 ROM ==========

    def _on_extract_rom(self):
        """解包 ROM —— 调用 dumpsxiso 解包到缓存目录"""
        rom_path = config.option.source_rom.value
        if not rom_path:
            w = MessageBox(
                self._msg_rom_path_not_set,
                self._msg_config_rom_path,
                self.window(),
            )
            w.exec()
            return

        if not os.path.isfile(rom_path):
            w = MessageBox(
                self._msg_file_not_found,
                self._msg_rom_not_exist.format(rom_path),
                self.window(),
            )
            w.yesButton.setText(self._msg_ok)
            w.cancelButton.hide()
            w.exec()
            return

        cache_path, xml_path = self._cache_paths()

        # 缓存目录已存在时确认覆盖
        if os.path.isdir(cache_path):
            w = MessageBox(
                self._msg_cache_exists,
                self._msg_cache_overwrite,
                self.window(),
            )
            w.yesButton.setText(self._msg_overwrite)
            w.cancelButton.setText(self._msg_cancel)
            if not w.exec():
                return

        os.makedirs(cache_path, exist_ok=True)

        dialog = ProgressDialog(self.window())
        dialog.set_button_text(self._close_text)
        dialog.start(DUMPSXISO, ["-x", cache_path, "-s", xml_path, rom_path])
        if dialog.exec():
            self._on_parse()

    # ========== 解析/构建缓存 ==========

    # ========== 解析缓存 ==========

    def _on_parse(self):
        """解析缓存：读取 XML 目录树 + 解析所有二进制数据"""
        cache_path, xml_path = self._cache_paths()
        if not os.path.isdir(cache_path):
            w = MessageBox(
                self._msg_file_not_found,
                self._msg_cache_dir_not_found,
                self.window(),
            )
            w.yesButton.setText(self._msg_ok)
            w.cancelButton.hide()
            w.exec()
            return

        self.tree.load_xml(xml_path)
        self.parseClicked.emit()

    # ========== 构建缓存 ==========

    def _on_build(self):
        """构建修改的数据到缓存文件"""
        w = MessageBox(
            self._msg_build_title,
            self._msg_build_confirm,
            self.window(),
        )
        w.yesButton.setText(self._msg_ok)
        w.cancelButton.setText(self._msg_cancel)
        if w.exec():
            self.buildClicked.emit()

    # ========== 重建 ROM ==========

    def _on_rebuild_rom(self):
        """重建 ROM —— 调用 mkpsxiso 从缓存目录重建镜像"""

        target_rom = config.option.target_rom.value
        if not target_rom:
            w = MessageBox(
                self._msg_target_rom_not_set,
                self._msg_config_target_rom,
                self.window(),
            )
            w.exec()
            return

        cache_path, xml_path = self._cache_paths()
        if not os.path.isfile(xml_path):
            w = MessageBox(
                self._msg_file_not_found,
                self._msg_cache_not_found,
                self.window(),
            )
            w.yesButton.setText(self._msg_ok)
            w.cancelButton.hide()
            w.exec()
            return

        output_bin = target_rom
        output_cue = os.path.splitext(output_bin)[0] + ".cue"

        if os.path.exists(output_bin):
            w = MessageBox(
                self._msg_file_exists,
                self._msg_overwrite_prompt.format(output_bin),
                self.window(),
            )
            w.yesButton.setText(self._msg_overwrite)
            w.cancelButton.setText(self._msg_cancel)
            if not w.exec():
                return

        dialog = ProgressDialog(self.window())
        dialog.set_button_text(self._close_text)
        dialog.start(MKPSXISO, ["-y", "-o", output_bin, "-c", output_cue, xml_path])
        if dialog.exec():
            os.startfile(os.path.dirname(output_bin))
            if config.option.auto_clean.value and os.path.isdir(cache_path):
                shutil.rmtree(cache_path, ignore_errors=True)

    # ========== 国际化 / 重置 ==========

    def translateUI(self):
        """更新界面文本翻译"""
        self._extract_rom_text = self.tr("Extract ROM")
        self._rebuild_rom_text = self.tr("Rebuild ROM")
        self._parse_cache_text = self.tr("Parse Cache")
        self._build_cache_text = self.tr("Build Cache")
        self._close_text = self.tr("Close")

        self._msg_rom_path_not_set = self.tr("ROM Path Not Configured")
        self._msg_config_rom_path = self.tr("Please configure the ROM file path in Settings first.")
        self._msg_file_not_found = self.tr("File Not Found")
        self._msg_rom_not_exist = self.tr("ROM file does not exist:\n{}")
        self._msg_ok = self.tr("OK")
        self._msg_target_rom_not_set = self.tr("Target ROM Not Configured")
        self._msg_config_target_rom = self.tr("Please configure the target ROM path in Settings first.")
        self._msg_cache_not_found = self.tr("Cache project file not found. Please extract a ROM first.")
        self._msg_cache_dir_not_found = self.tr("Cache directory not found. Please extract a ROM first.")
        self._msg_cache_exists = self.tr("Cache already exists. Overwrite?")
        self._msg_cache_overwrite = self.tr("The cache directory already exists. Do you want to overwrite it?")
        self._msg_overwrite = self.tr("Overwrite")
        self._msg_cancel = self.tr("Cancel")
        self._msg_build_title = self.tr("Build Cache")
        self._msg_build_confirm = self.tr("Are you sure you want to build modified data to cache files?")
        self._msg_file_exists = self.tr("File Already Exists")
        self._msg_overwrite_prompt = self.tr("The output file already exists:\n{}\n\nDo you want to overwrite it?")
        self._msg_yes = self.tr("Yes")
        self._msg_no = self.tr("No")

        self.extract_button.setText(self._extract_rom_text)
        self.rebuild_button.setText(self._rebuild_rom_text)
        self.parse_button.setText(self._parse_cache_text)
        self.build_button.setText(self._build_cache_text)

        # 刷新树表头与分类映射（self.tr() 值随语言切换变化）
        self._headers = [
            self.tr("File"),
            self.tr("Robot"),
            self.tr("Pilot"),
            self.tr("Message"),
            self.tr("Scenario"),
            self.tr("Intermission"),
            self.tr("Dictionary"),
        ]
        self._datas = {
            self.tr("Robot"): ["ROBOT.RAF"],
            self.tr("Pilot"): ["PILOT.BIN"],
            self.tr("Message"): ["SNMSG.BIN"],
            self.tr("Scenario"): [
                "ROBOT.RAF",
                "PILOT.BIN",
                "SNMSG.BIN",
                "SNDATA.BIN",
                "ENLIST.BIN",
                "AIUNP.BIN",
            ],
            self.tr("Intermission"): [
                "SCRIPT.BIN",
            ],
            self.tr("Dictionary"): ["DR.BIN", "DC.BIN"],
        }
        self.tree.setHeaderLabels(self._headers)

    def resetUI(self):
        """重置界面字体"""
        setFont(self.extract_button, 18)
        setFont(self.rebuild_button, 18)
        setFont(self.parse_button, 18)
        setFont(self.build_button, 18)
        self.tree.resetUI()
