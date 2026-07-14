"""
SNDATA.BIN 解析/构建 往返测试

测试内容：
  1. 解析 SNDATA.BIN → Python dict
  2. 将 dict 重建为二进制
  3. 逐字节对比重建后与原始文件
  4. 验证区块指针动态计算正确性
  5. 验证各场景 BLOCK 分布
"""

import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.sndata_bin import build, parse

RES_BIN = os.path.join(os.path.dirname(__file__), "..", "res", "bin")
SNDATA_PATH = os.path.join(RES_BIN, "SNDATA.BIN")

SCENARIO_COUNT = 0x8C
BLOCK_QTY = 0x10


def main() -> int:
    """执行往返测试：解析 → 重建 → 逐字节对比"""
    print()
    print("  ╔═══════════════════════════════════════════╗")
    print("  ║      SNDATA.BIN 往返一致性测试            ║")
    print("  ╚═══════════════════════════════════════════╝")
    print()

    if not os.path.isfile(SNDATA_PATH):
        print(f"  [WARN] 文件不存在: {SNDATA_PATH}")
        print()
        print("  请将 SNDATA.BIN 放入 res/bin/ 目录后重试。")
        return 0

    fsize = os.path.getsize(SNDATA_PATH)
    print(f"  [INFO] 文件: {SNDATA_PATH}")
    print(f"  [INFO] 大小: {fsize} bytes (0x{fsize:X})")
    print()

    with open(SNDATA_PATH, "rb") as f:
        original = f.read()

    # 1. 解析
    print("  ── 解析 ──")
    data = parse(original)
    scenarios = data["scenarios"]
    print(f"  [INFO] 场景数: {len(scenarios)}")
    total_cmds = sum(len(s["commands"]) for s in scenarios)
    print(f"  [INFO] 总指令数: {total_cmds}")
    print()

    # 2. 打印前 3 场景概要
    print("  ── 前 3 场景概要 ──")
    for i in range(min(3, len(scenarios))):
        sc = scenarios[i]
        cmds = sc["commands"]
        blocks = [
            c["params"][0]
            for c in cmds
            if c["code"] == 0x00 and len(c["params"]) > 0
        ]
        print(f"  [{i}] {len(cmds)} 条指令, {len(blocks)} 个 BLOCK ({blocks})")
    print()

    # 3. 重建并逐字节对比
    print("  ── 重建 → 逐字节对比 ──")
    rebuilt = build(data)
    print(f"  [INFO] 重建大小: {len(rebuilt)} bytes")

    if len(original) != len(rebuilt):
        print(
            f"  [ERROR] 大小不一致: 原始 {len(original)} vs 重建 {len(rebuilt)}"
        )
        return 1

    diffs = 0
    first_diff = -1
    for i in range(len(original)):
        if original[i] != rebuilt[i]:
            diffs += 1
            if first_diff < 0:
                first_diff = i

    if diffs:
        print(f"  [ERROR] 共有 {diffs} 处差异")
        print(f"         首差异 @ 字节 {first_diff} (0x{first_diff:X})")
        print(
            f"         原始 0x{original[first_diff]:02X} vs 重建 0x{rebuilt[first_diff]:02X}"
        )
        return 1

    print("  [INFO] 逐字节完全相同")
    print()

    # 4. 验证区块指针与原始一致（动态计算正确性）
    print("  ── 区块指针验证 ──")
    bad_ptrs = 0
    for i in range(SCENARIO_COUNT):
        ptr = struct.unpack_from("<I", original, i * 4)[0]
        orig_ptrs = list(struct.unpack_from("<16I", original, ptr + 8))
        our_ptrs = scenarios[i]["block_pointers"]
        for j in range(BLOCK_QTY):
            if (orig_ptrs[j] & 0xFFFFFFFF) != (our_ptrs[j] & 0xFFFFFFFF):
                bad_ptrs += 1
                if bad_ptrs <= 3:
                    print(
                        f"  [ERROR] 场景 {i} 指针[{j}]: "
                        f"原始 0x{orig_ptrs[j]:08X} vs "
                        f"重建 {our_ptrs[j] & 0xFFFFFFFF:08X}"
                    )

    if bad_ptrs:
        print(f"  [ERROR] 共 {bad_ptrs} 处指针不一致")
        return 1
    print("  [INFO] 全部区块指针一致")
    print()

    # 5. 验证 BLOCK 数量
    print("  ── BLOCK 分布验证 ──")
    for i in range(min(5, len(scenarios))):
        cmds = scenarios[i]["commands"]
        blocks = [c for c in cmds if c["code"] == 0x00 and len(c["params"]) > 0]
        block_ids = [c["params"][0] for c in blocks]
        print(
            f"  [{i}] {len(cmds)} 条指令, BLOCK IDs: "
            f"{[b for b in block_ids if 0 <= b <= 0x0A]}"
        )
    print()

    print("  ═══════════════════════════════════════════")
    print("   [INFO] ALL TESTS PASSED")
    print("  ═══════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
