"""
数据代理框体 - 负责 set_model/set_row 转发与 widget 编排

ProxyFrame 提供 translateUI/resetUI 自动传播；
CardHeader 提供卡片标题与 panelDataChanged 信号。

Classes:
    ProxyFrame / CardHeader
"""

from .card_header import CardHeader
from .proxy_frame import ProxyFrame
