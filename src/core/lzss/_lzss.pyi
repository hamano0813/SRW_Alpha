"""
LZSS compression / decompression (native C extension)
"""

from typing import Optional

def compress(raw_data: bytearray, pack: int = 1) -> bytearray:
    """Compress raw data using LZSS.

    Args:
        raw_data: Input bytearray to compress.
        pack: Output alignment (1 = no padding, 2/4/8 = align to boundary).

    Returns:
        Compressed bytearray.

    Raises:
        RuntimeError: If compression fails.
    """
    ...

def decompress(comp_data: bytearray) -> bytearray:
    """Decompress LZSS data.

    Args:
        comp_data: Compressed bytearray.

    Returns:
        Decompressed bytearray.

    Raises:
        RuntimeError: If decompression fails.
    """
    ...
