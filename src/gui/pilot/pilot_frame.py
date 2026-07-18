"""
驾驶员编辑框架模块（待实现）

提供驾驶员数据的表格展示和编辑界面，配合 PILOT.BIN 解析模块使用。
当前为空框架，待后续填充具体内容。

Classes:
    PilotFrame: 驾驶员编辑框架
"""

from gui.custom.proxy_frame import ProxyFrame


class PilotFrame(ProxyFrame):
    """驾驶员编辑框架（待实现）"""

    def __init__(self, fields, parent=None):
        """初始化驾驶员编辑框架

        Args:
            fields: FieldMapping 字段映射实例
            parent: 父 QWidget
        """
        super().__init__(parent)
        self.setObjectName("PilotFrame")

        self._rom_data: dict | None = None
