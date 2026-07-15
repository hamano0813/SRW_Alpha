"""
DR.BIN 解析/构建 往返测试

测试内容：
  1. 解析 DR.BIN → Python dict
  2. 验证名册与机体数据完整性
  3. 重建为二进制并重新解析
  4. 逐条数据一致性对比
  5. 逐字节对比全部 449 块（严格模式）
  6. 压缩大小差异统计
"""

import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.codec.extra import DR_TEXT_EXTRA
from core.dr_bin import build, parse

RES_BIN = os.path.join(os.path.dirname(__file__), "..", "res", "bin")
DR_PATH = os.path.join(RES_BIN, "DR.BIN")


def main() -> int:
    """执行往返测试"""
    print()
    print("  ╔═══════════════════════════════════════════╗")
    print("  ║      DR.BIN 往返一致性测试                ║")
    print("  ╚═══════════════════════════════════════════╝")
    print()

    if not os.path.isfile(DR_PATH):
        print(f"  [WARN] 文件不存在: {DR_PATH}")
        print()
        print("  请将 DR.BIN 放入 res/bin/ 目录后重试。")
        return 0

    fsize = os.path.getsize(DR_PATH)
    print(f"  [INFO] 文件: {DR_PATH}")
    print(f"  [INFO] 大小: {fsize} bytes (0x{fsize:X})")
    print()

    with open(DR_PATH, "rb") as f:
        original = f.read()

    # 1. 第一次解析（带 SPECIAL_TEXT_EXTRA 验证字段）
    print("  ── 第 1 次解析 ──")
    data1 = parse(original, extra=DR_TEXT_EXTRA)
    roster1 = data1["roster"]
    dr_list1 = data1["dr"]
    count = data1["count"]
    print(f"  [INFO] 机体数: {count}")
    print(f"  [INFO] 名册条目: {len(roster1)}")
    print()

    # 2. 验证数据完整性
    assert len(roster1) == 448
    assert len(dr_list1) == 448
    assert count == 448

    # 验证名册前 3 条
    expected_names = [
        "ヒュッケバインMK-II",
        "ヒュッケバインMK-III",
        "ヒュッケバインボクサー",
    ]
    for i, expected in enumerate(expected_names):
        if roster1[i] != expected:
            print(f"  [ERROR] 名册[{i}]: 期望 '{expected}' 实际 '{roster1[i]}'")
            return 1
    print(f"  [INFO] 名册前 3 条验证通过")

    # 验证首条机体关键字段
    r0 = dr_list1[0]
    assert r0["name"] == "ヒュッケバインMK-II"
    assert r0["height"] == "20.8m"
    assert r0["weight"] == "52.0t"
    assert r0["appr"] == "オリジナル"
    assert r0["flags"] == 0x15
    assert len(r0["desc"]) > 200
    print(f"  [INFO] 块1(ヒュッケバインMK-II) 字段验证通过")
    print()

    # 3. 重建并重新解析（带 DR_TEXT_EXTRA，验证编码对称性）
    print("  ── 重建 → 第 2 次解析 ──")
    rebuilt = build(data1, extra=DR_TEXT_EXTRA)
    print(f"  [INFO] 重建大小: {len(rebuilt)} bytes (原始 {fsize} bytes)")
    data2 = parse(rebuilt, extra=DR_TEXT_EXTRA)
    assert data2["count"] == count
    print()

    # 4. 逐条数据对比
    print("  ── 数据一致性对比 ──")
    all_ok = True
    for i in range(count):
        for key in ("name", "height", "weight", "appr", "flags", "desc"):
            if data1["dr"][i][key] != data2["dr"][i][key]:
                print(f"  [ERROR] dr[{i}].{key} 不一致")
                all_ok = False
    for i in range(len(roster1)):
        if data1["roster"][i] != data2["roster"][i]:
            print(f"  [ERROR] 名册[{i}] 不一致")
            all_ok = False
    if all_ok:
        print(f"  [INFO] 全部 {count} 条机体数据一致")
        print(f"  [INFO] 名册 {len(roster1)} 条一致")
    else:
        return 1
    print()

    # 5. 逐字节对比（严格模式：全部 449 块）
    print("  ── 逐字节对比 ──")
    orig_ptrs = [struct.unpack_from("<I", original, i * 4)[0] for i in range(450)]
    rebuilt_ptrs = [struct.unpack_from("<I", rebuilt, i * 4)[0] for i in range(450)]

    byte_diff_blocks = []
    for blk in range(449):
        orig_blk = original[orig_ptrs[blk] : orig_ptrs[blk + 1]]
        rebuilt_blk = rebuilt[rebuilt_ptrs[blk] : rebuilt_ptrs[blk + 1]]
        if orig_blk != bytes(rebuilt_blk):
            byte_diff_blocks.append(blk)

    if byte_diff_blocks:
        print(f"  [ERROR] 逐字节不一致的块: {len(byte_diff_blocks)} / 449")
        for blk in byte_diff_blocks[:20]:
            o_size = orig_ptrs[blk + 1] - orig_ptrs[blk]
            r_size = rebuilt_ptrs[blk + 1] - rebuilt_ptrs[blk]
            note = ""
            if o_size != r_size:
                note = f" (大小: {o_size}→{r_size}, {r_size - o_size:+d}B)"
            else:
                note = " (内容不同)"
            print(f"    [{blk:3d}]{note}")
        if len(byte_diff_blocks) > 20:
            print(f"    ... 及 {len(byte_diff_blocks) - 20} 个")
        print()
        return 1

    print(f"  [INFO] 全部 449 块逐字节完全相同")
    print()

    # 6. 压缩大小统计
    print("  ── 压缩大小差异统计 ──")
    print(
        f"  [INFO] 总文件: 原始 {len(original)} vs 重建 {len(rebuilt)} "
        f"({'+' if len(rebuilt) >= len(original) else ''}{len(rebuilt) - len(original)} bytes)"
    )

    size_diffs = []
    for blk in range(449):
        o_size = orig_ptrs[blk + 1] - orig_ptrs[blk]
        r_size = rebuilt_ptrs[blk + 1] - rebuilt_ptrs[blk]
        diff = r_size - o_size
        if diff != 0:
            size_diffs.append((blk, o_size, r_size, diff))

    if size_diffs:
        print(f"  [INFO] 压缩大小不一致的块: {len(size_diffs)} 个")
        for blk, o, r, d in size_diffs:
            print(f"    [{blk:3d}] 原始 {o:5d} → 重建 {r:5d}  ({d:+d})")
    else:
        print(f"  [INFO] 全部 449 块压缩大小完全一致")
    print()

    print("  ═══════════════════════════════════════════")
    print("   [INFO] ALL TESTS PASSED")
    print("  ═══════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
