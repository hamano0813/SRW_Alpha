import os
import sys

__dir__ = os.path.dirname(__file__)
if __dir__ not in sys.path:
    sys.path.insert(0, __dir__)

from ._lzss import compress, decompress

__all__ = ["compress", "decompress"]
