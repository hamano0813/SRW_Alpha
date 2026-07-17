"""
工具函数包

导出字体工具和系统工具函数。

Functions:
    get_font_info: 获取字体显示名称
    get_font_mapping: 获取字体映射表
    best_resolution: 获取最佳屏幕分辨率
    restart: 重启应用程序
"""

from .font import get_font_info, get_font_mapping
from .system import best_resolution, restart

__all__ = ["get_font_info", "get_font_mapping", "restart", "best_resolution"]
