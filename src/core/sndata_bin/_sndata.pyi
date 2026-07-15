"""
SNDATA.BIN 类型存根
"""

from typing import Any, Optional


def parse(
    data: bytes | bytearray,
    extra: Optional[dict[str, str]] = None,
) -> dict[str, Any]:
    """解析 SNDATA.BIN 为 Python dict

    Args:
        data: 原始二进制数据
        extra: 忽略（SNDATA 无文本编码，仅用于 API 一致性）

    Returns:
        dict: {
            "scenarios": [
                {
                    "block_pointers": list[int],  # 16 个区块指针值
                    "commands": list[dict],        # 指令列表，每条含 code/count/params + explain（空字符串预留）
                },
            ]
        }
    """


def build(
    data: dict[str, Any],
    extra: Optional[dict[str, str]] = None,
) -> bytearray:
    """从 Python dict 构建 SNDATA.BIN 二进制

    Args:
        data: parse 返回的 dict
        extra: 忽略

    Returns:
        bytearray: SNDATA.BIN 二进制数据
    """
