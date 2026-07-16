"""
缓存数据导出测试

测试内容：
  1. 读取缓存目录中的全部已注册数据文件
  2. 将解析后的数据导出为文本（供人工审查/调试）
"""

import os
import pprint
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import config
from core.rom import Rom

# 导出目录（在项目根下，已加入 .gitignore）
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "_test_cache")


def main() -> int:
    """读取缓存并导出为文本"""
    rom = Rom()

    print(f"[INFO] 缓存目录: {rom.cache_dir}")
    rom.parse_cache()

    # ========== 导出为 TXT ==========

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for key in rom.data:
        data = rom.data[key]
        basename = os.path.splitext(os.path.basename(rom._FILE_PATHS[key]))[0]
        fname = basename + ".txt"
        path = os.path.join(OUTPUT_DIR, fname)

        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# {rom._FILE_PATHS[key]}\n")
            f.write(f"# 条目数: {data.get('count', '?')}\n\n")
            f.write(pprint.pformat(data, indent=2, width=120, sort_dicts=False))
            f.write("\n")

        print(f"  [INFO] {fname} 已导出")

    print(f"[INFO] 导出完成，共 {len(rom.data)} 个文件")
    return 0


if __name__ == "__main__":
    sys.exit(main())
