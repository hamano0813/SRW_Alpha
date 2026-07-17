"""
系统工具函数模块

提供应用程序重启、屏幕分辨率计算等系统级实用功能。

Functions:
    restart: 重启当前应用程序
    best_resolution: 获取当前屏幕的最佳初始分辨率
"""

import ctypes
import os
import sys

_BASE_WIDTH = 320
_BASE_HEIGHT = 240


def restart():
    """重启当前应用程序"""
    exe = sys.executable
    argv = [exe] + sys.argv
    os.execv(exe, argv)


def best_resolution() -> tuple[int, int]:
    """获取当前屏幕的最佳初始分辨率

    以 320×240 为基准，取最大的整数倍使垂直分辨率不超过
    屏幕高度减去任务栏预留高度（50px）。

    Returns:
        (width, height): 最佳分辨率
    """
    user32 = ctypes.windll.user32
    screen_height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
    max_height = screen_height - 50
    multiplier = max_height // _BASE_HEIGHT
    return (multiplier * _BASE_WIDTH, multiplier * _BASE_HEIGHT)
