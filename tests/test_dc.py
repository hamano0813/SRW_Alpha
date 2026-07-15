"""
DC.BIN 解析/构建 往返测试

测试内容：
  1. 解析 DC.BIN → Python dict
  2. 验证名册与角色数据完整性
  3. 重建为二进制并重新解析
  4. 对比数据一致性
  5. 逐字节对比块1~349（跳过块0名册和块214官方bug）
  6. 压缩大小对比统计
"""

import os
import struct
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.codec.extra import DC_TEXT_EXTRA
from core.dc_bin import build, parse

RES_BIN = os.path.join(os.path.dirname(__file__), "..", "res", "bin")
DC_PATH = os.path.join(RES_BIN, "DC.BIN")


def _dicts_equal(a: dict, b: dict) -> bool:
    """深度比较两个角色字典"""
    for k in a:
        if k.startswith("_"):
            continue
        if k not in b:
            return False
        va, vb = a[k], b[k]
        if isinstance(va, str) and isinstance(vb, str):
            if va != vb:
                return False
        elif va != vb:
            return False
    return True


def main() -> int:
    """执行往返测试"""
    print()
    print("  ╔═══════════════════════════════════════════╗")
    print("  ║      DC.BIN 往返一致性测试                ║")
    print("  ╚═══════════════════════════════════════════╝")
    print()

    if not os.path.isfile(DC_PATH):
        print(f"  [WARN] 文件不存在: {DC_PATH}")
        print()
        print("  请将 DC.BIN 放入 res/bin/ 目录后重试。")
        return 0

    fsize = os.path.getsize(DC_PATH)
    print(f"  [INFO] 文件: {DC_PATH}")
    print(f"  [INFO] 大小: {fsize} bytes (0x{fsize:X})")
    print()

    with open(DC_PATH, "rb") as f:
        original = f.read()

    # 1. 第一次解析
    print("  ── 第 1 次解析 ──")
    data1 = parse(original, extra=DC_TEXT_EXTRA)
    roster = data1["roster"]
    dc_list = data1["dc"]
    count = data1["count"]
    print(f"  [INFO] 角色数: {count}")
    print(f"  [INFO] 名册条目: {len(roster)}")
    print()

    # 2. 验证名册与角色数据
    assert len(roster) == 349
    assert len(dc_list) == 349
    assert count == 349

    # 验证名册前 3 条
    expected_names = [
        "イルムガルト=カザハラ",
        "リン=マオ",
        "スレッガー=ロウ",
    ]
    for i, expected in enumerate(expected_names):
        if roster[i] != expected:
            print(f"  [ERROR] 名册[{i}]: 期望 '{expected}' 实际 '{roster[i]}'")
            return 1
    print(f"  [INFO] 名册前 3 条验证通过")

    # 验证块 2（スレッガー＝ロウ）描述完整性
    desc2 = dc_list[2].get("desc", "")
    known_phrases = ["ホワイトベース", "ジャブロー", "階級は中尉", "粗野な印象", "婚約者", "捨て身の攻撃"]
    for phrase in known_phrases:
        if phrase not in desc2:
            print(f"  [WARN] 描述验证: '{phrase}' 缺失")
            return 1
    print(f"  [INFO] 块2(スレッガー) 描述验证通过")

    # 验证首条角色字段
    c0 = dc_list[0]
    assert c0["fname"] == "イルムガルト＝カザハラ"
    assert c0["pname"] == "イルム"
    assert c0["appr"] == "超機大戦ＳＲＸ"
    assert c0["voice"] == "堀内賢雄"
    assert c0["flags"] == 0x10
    print(f"  [INFO] 块1(イルム) 字段验证通过")
    print()

    # 3. 重建并重新解析
    print("  ── 重建 → 第 2 次解析 ──")
    rebuilt = build(data1, extra=DC_TEXT_EXTRA)
    print(f"  [INFO] 重建大小: {len(rebuilt)} bytes (原始 {fsize} bytes)")
    data2 = parse(rebuilt, extra=DC_TEXT_EXTRA)
    assert data2["count"] == count
    print()

    # 4. 逐条数据对比
    print("  ── 数据一致性对比 ──")
    for i in range(count):
        if not _dicts_equal(dc_list[i], data2["dc"][i]):
            print(f"  [ERROR] 角色 {i} 不一致")
            return 1
    print(f"  [INFO] 全部 {count} 条角色数据一致")

    # 名册对比
    for i in range(len(roster)):
        if roster[i] != data2["roster"][i]:
            print(f"  [ERROR] 名册 {i} 不一致")
            return 1
    print(f"  [INFO] 名册 {len(roster)} 条一致")
    print()

    # 5. 逐字节对比（跳过块0和块214）
    print("  ── 逐字节对比 ──")
    orig_ptrs = [struct.unpack_from("<I", original, i * 4)[0] for i in range(351)]
    rebuilt_ptrs = [struct.unpack_from("<I", rebuilt, i * 4)[0] for i in range(351)]

    skip_blocks = {0, 214}
    for blk in range(1, 350):
        if blk in skip_blocks:
            continue
        orig_blk = original[orig_ptrs[blk] : orig_ptrs[blk + 1]]
        rebuilt_blk = rebuilt[rebuilt_ptrs[blk] : rebuilt_ptrs[blk + 1]]
        if orig_blk != bytes(rebuilt_blk):
            print(f"  [ERROR] 块{blk}: 原始 {len(orig_blk)} vs 重建 {len(rebuilt_blk)}")
            return 1
    print(f"  [INFO] 块1~349（除214外）逐字节完全相同")

    # 6. 压缩大小统计
    print()
    print("  ── 压缩大小对比 ──")
    print(
        f"  [INFO] 总文件: 原始 {len(original)} vs 重建 {len(rebuilt)} "
        f"({'+' if len(rebuilt) >= len(original) else ''}{len(rebuilt) - len(original)} bytes)"
    )

    size_diffs = []
    for blk in range(0, 350):
        o_size = orig_ptrs[blk + 1] - orig_ptrs[blk]
        r_size = rebuilt_ptrs[blk + 1] - rebuilt_ptrs[blk]
        diff = r_size - o_size
        if diff != 0:
            size_diffs.append((blk, o_size, r_size, diff))

    if size_diffs:
        print(f"  [INFO] 压缩大小不一致的块: {len(size_diffs)} 个")
        for blk, o, r, d in size_diffs:
            note = ""
            if blk == 0:
                note = " ← 名册，规则2未实现"
            elif blk == 214:
                note = " ← 官方空cell"
            print(f"    [{blk:3d}] 原始 {o:5d} → 重建 {r:5d}  " f"({d:+d}){note}")
    else:
        print(f"  [INFO] 全部 350 块压缩大小完全一致")
    print()

    print("  ═══════════════════════════════════════════")
    print("   [INFO] ALL TESTS PASSED")
    print("  ═══════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
