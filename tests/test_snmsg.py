"""
SNMSG.BIN 解析/构建 往返测试

测试内容：
  1. 解析 SNMSG.BIN → Python dict（带 SNMSG_TEXT_EXTRA 映射）
  2. 将 dict 重建为二进制
  3. 重新解析重建后的二进制 → Python dict
  4. 对比两次解析的 dict 是否一致（数据完整性）
  5. 对比重建后的文件大小与原始文件大小
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


from core.codec.extra import SNMSG_TEXT_EXTRA
from core.snmsg_bin import build, parse

RES_BIN = os.path.join(os.path.dirname(__file__), "..", "res", "bin")
SNMSG_BIN_PATH = os.path.join(RES_BIN, "SNMSG.BIN")


def main() -> int:
    """执行往返测试：解析 → 重建 → 再解析 → 对比数据"""
    print()
    print("  ╔═══════════════════════════════════════════╗")
    print("  ║      SNMSG.BIN 往返一致性测试              ║")
    print("  ╚═══════════════════════════════════════════╝")
    print()

    if not os.path.isfile(SNMSG_BIN_PATH):
        print(f"  [WARN] 文件不存在: {SNMSG_BIN_PATH}")
        print()
        print("  请将 SNMSG.BIN 放入 res/bin/ 目录后重试。")
        return 0

    fsize = os.path.getsize(SNMSG_BIN_PATH)
    print(f"  文件: {SNMSG_BIN_PATH}")
    print(f"  大小: {fsize} bytes (0x{fsize:X})")
    print(f"  条目: {fsize // 0x100}")
    print()

    with open(SNMSG_BIN_PATH, "rb") as f:
        original = f.read()

    # 1. 第一次解析（带 extra 映射）
    print("  ── 第 1 次解析（extra 映射）──")
    data1 = parse(bytearray(original), extra=SNMSG_TEXT_EXTRA)
    count = data1["count"]
    msgs1 = data1["snmsgs"]
    print(f"  消息数: {count}")
    assert count == len(msgs1)
    print("  [INFO]")
    print()

    # 2. 打印前 3 条消息
    print("  ── 前 3 条消息 ──")
    for i in range(min(3, count)):
        text = msgs1[i]
        # 截断过长显示
        preview = text[:30] + "..." if len(text) > 30 else text
        print(f"  [{i}] {preview}")
    print()

    # 3. 重建并重新解析（带 extra 映射）
    print("  ── 重建 → 第 2 次解析（extra 映射）──")
    rebuilt = build(data1, extra=SNMSG_TEXT_EXTRA)
    print(f"  重建大小: {len(rebuilt)} bytes (原始 {fsize} bytes)")
    data2 = parse(rebuilt, extra=SNMSG_TEXT_EXTRA)
    msgs2 = data2["snmsgs"]
    assert data2["count"] == count
    print("  [INFO]")
    print()

    # 4. 逐条深入对比
    print("  ── 数据一致性对比 ──")
    all_ok = True
    for i in range(count):
        if msgs1[i] != msgs2[i]:
            print(f"  [ERROR] 条目 {i} 不一致")
            print(f"          原始: {repr(msgs1[i][:50])}")
            print(f"          重建: {repr(msgs2[i][:50])}")
            all_ok = False
            break

    if not all_ok:
        print()
        return 1

    print(f"  [INFO] 全部 {count} 条消息数据一致")
    print()

    # 5. 大小对比
    print("  ── 文件大小对比 ──")
    if len(original) == len(rebuilt):
        print("  [INFO] 大小一致")
    else:
        print(f"  [WARN] 原始 {len(original)} bytes, 重建 {len(rebuilt)} bytes")
    print()
    print("  ═══════════════════════════════════════════")
    print("   ALL TESTS PASSED")
    print("  ═══════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
