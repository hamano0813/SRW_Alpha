"""
驾驶员编辑框架模块

提供驾驶员数据的表格展示和编辑界面，配合 PILOT.BIN 解析模块使用。
参照 robot_frame.py 的模式实现。

左侧：PilotTable 驾驶员表格
右侧：PilotPanel 各编辑卡片

Classes:
    PilotFrame: 驾驶员编辑框架（可平滑滚动）
"""

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QHBoxLayout
from qfluentwidgets import SmoothScrollArea

from gui.widget import BaseTableModel, ProxyFrame
from gui.interface.pilot.pilot_panel import PilotPanel
from gui.interface.pilot.pilot_table import PilotTable


class PilotFrame(SmoothScrollArea):
    """驾驶员编辑框架 - 驾驶员表格 + 编辑卡片联动（可平滑滚动）"""

    def __init__(
        self,
        fields,
        parent=None,
    ):
        """初始化驾驶员编辑框架

        Args:
            fields: FieldMapping 字段映射实例
            parent: 父 QWidget
        """
        super().__init__(parent)
        self.setObjectName("PilotFrame")
        self.setWidgetResizable(False)
        self.enableTransparentBackground()

        self._rom_data: dict | None = None
        self._current_source_row: int = -1

        # ========== 容器（水平布局：驾驶员表格 | 右侧面板） ==========

        self._container = ProxyFrame()
        self._container.resize(800, 32)
        self.setWidget(self._container)

        layout = QHBoxLayout(self._container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ===== 左侧：驾驶员表格 =====

        self._pilot_table = PilotTable(self._container)
        self._pilot_table.set_field(fields)
        layout.addWidget(self._pilot_table, 1)

        # ===== 右侧：编辑面板 =====

        self._pilot_panel = PilotPanel(self._container)
        self._pilot_panel.panelDataChanged.connect(self._on_panel_data_changed)
        layout.addWidget(self._pilot_panel)

        # 默认隐藏右侧面板
        self._pilot_panel.setVisible(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._pilot_table.sClicked.connect(self._on_row_clicked)

    # ========== 全局定位 ==========

    def _update_layout(self):
        """根据面板可见性调整容器尺寸"""
        vp_w = self.viewport().width()
        vp_h = self.viewport().height()
        if vp_w <= 0 or vp_h <= 0:
            win = self.window()
            if win and win.isVisible():
                vp_w = win.width() - 100
                vp_h = win.height() - 100
                if vp_w <= 0:
                    vp_w = 1000
                if vp_h <= 0:
                    vp_h = 600
            else:
                return

        self._container.resize(vp_w, vp_h)

    def resizeEvent(self, event):
        """窗口缩放后刷新布局"""
        super().resizeEvent(event)
        QTimer.singleShot(0, self._update_layout)

    # ========== 行点击 ==========

    def _on_row_clicked(self, source_row: int, model: BaseTableModel) -> None:
        """行点击时显示面板并切换数据

        Args:
            source_row: 源模型行号
            model:      BaseTableModel 实例
        """
        self._current_source_row = source_row

        # 首次点击时显示右侧面板
        if not self._pilot_panel.isVisible():
            self._pilot_panel.setVisible(True)
            QTimer.singleShot(0, self._update_layout)

        self._pilot_panel.set_model(model)
        self._pilot_panel.set_row(source_row)

    # ========== 面板编辑回写 ==========

    def _on_panel_data_changed(self, field: str) -> None:
        """面板编辑器修改数据后通知 model 刷新对应单元格

        Args:
            field: 被修改的字段名
        """
        model = self._pilot_table.pilot_view.source_model()
        for col, header in enumerate(model.headers):
            if model.fields.get_field(header) == field:
                idx = model.index(self._current_source_row, col)
                model.dataChanged.emit(idx, idx, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])
                break

    # ========== 数据解析 ==========

    def set_rom_data(self, data: dict) -> None:
        """装入 ROM 的驾驶员数据

        Args:
            data: Rom().parse_pilots() 返回的 dict，
                  包含 "pilots" 列表
        """
        self._rom_data = data
        pilots = data.get("pilots", {})
        self._pilot_table.set_data(pilots.get("pilots", []))

        # 默认选中第一行
        model = self._pilot_table.pilot_view.source_model()
        if model.rowCount() > 0:
            self._pilot_table.pilot_view.selectRow(0)
            self._on_row_clicked(0, model)

        self._update_layout()

    # ========== 主题与翻译 ==========

    def resetUI(self):
        """刷新所有子控件并更新布局"""
        self._container.resetUI()
        self._pilot_panel.resetUI()
        self._update_layout()

    def translateUI(self):
        """刷新所有子控件翻译并更新布局"""
        self._container.translateUI()
        self._pilot_table.translateUI()
        self._pilot_panel.translateUI()
        self._update_layout()
