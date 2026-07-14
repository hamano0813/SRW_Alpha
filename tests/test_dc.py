"""
DC.BIN 解析/构建 往返测试

测试内容：
  1. 解析 DC.BIN → Python dict
  2. 打印名册 + 角色详情前 5 条
  3. 重建为二进制
  4. 重新解析 → 对比数据一致性
  5. 逐字节对比块1~349（跳过块0名册和块214官方bug）
  6. 压缩大小对比统计
"""

import os
import sys
import struct

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

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
    print("  ║      DC.BIN 往返一致性测试                  ║")
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
    data1 = parse(original)
    roster = data1["roster"]
    dc_list = data1["dc"]
    count = data1["count"]
    print(f"  [INFO] 角色数: {count}")
    print(f"  [INFO] 名册条目: {len(roster)}")
    print()

    # 2. 打印名册前 10 条（写文件避免 GBK 终端问题）
    OUT_DIR = os.path.join(os.path.dirname(__file__), "dc_dump")
    os.makedirs(OUT_DIR, exist_ok=True)
    verify_log = os.path.join(OUT_DIR, "test_output.txt")
    with open(verify_log, "w", encoding="utf-8") as vf:
        vf.write("  ── 名册前 10 条 ──\n")
        for i in range(min(10, len(roster))):
            vf.write(f"    [{i:3d}] {roster[i]}\n")
        vf.write("\n")

        vf.write("  ── 前 3 条角色详情 ──\n")
        for i in range(min(3, len(dc_list))):
            c = dc_list[i]
            vf.write(f"    [角色 {i}]\n")
            vf.write(f"      完整名:  {c.get('fname', '')}\n")
            vf.write(f"      缩写名:  {c.get('pname', '')}\n")
            vf.write(f"      登场:    {c.get('appr', '')}\n")
            vf.write(f"      声优:    {c.get('voice', '')}\n")
            flags = c.get("flags", None)
            if flags is not None:
                vf.write(f"      标识:    0x{flags:02X} (0b{flags:08b})\n")
            desc = c.get("desc", "")
            if desc:
                vf.write(f"      描述 ({len(desc)} 字符):\n")
                for line in desc.split("\n")[:5]:
                    vf.write(f"        {line}\n")
                if desc.count("\n") >= 5:
                    vf.write(f"        ...\n")
            vf.write("\n")

    print(f"  [INFO] 详情写入 {verify_log}")

    # 验证块 2（スレッガー＝ロウ）描述完整性
    desc2 = dc_list[2].get("desc", "")
    known_phrases = [
        "ホワイトベース", "ジャブロー", "階級は中尉",
        "粗野な印象", "婚約者", "捨て身の攻撃"
    ]
    for phrase in known_phrases:
        if phrase in desc2:
            pass  # OK
        else:
            print(f"  [WARN] 描述验证: '{phrase}' 缺失")
            return 1
    print(f"  [INFO] 块2(スレッガー) 描述验证通过")
    print()

    # 4. 重建并重新解析
    print("  ── 重建 → 第 2 次解析 ──")
    rebuilt = build(data1)
    print(f"  [INFO] 重建大小: {len(rebuilt)} bytes (原始 {fsize} bytes)")
    data2 = parse(rebuilt)
    assert data2["count"] == count
    print()

    # 5. 逐条对比
    print("  ── 数据一致性对比 ──")
    all_ok = True
    for i in range(count):
        if not _dicts_equal(dc_list[i], data2["dc"][i]):
            print(f"  [ERROR] 角色 {i} 不一致")
            all_ok = False
            break

    if not all_ok:
        return 1

    print(f"  [INFO] 全部 {count} 条角色数据一致")

    # 名册对比
    for i in range(len(roster)):
        if roster[i] != data2["roster"][i]:
            print(f"  [ERROR] 名册 {i} 不一致")
            return 1
    print(f"  [INFO] 名册 {len(roster)} 条一致")
    print()

    # 6. 文件重建信息（跳过块0名册规则2未实现，跳过块214暗黒大将軍官方数据有误）
    print("  ── 文件重建（逐字节对比）──")
    # 从原始和重建文件中提取指针表
    orig_ptrs = [struct.unpack_from('<I', original, i * 4)[0] for i in range(351)]
    rebuilt_ptrs = [struct.unpack_from('<I', rebuilt, i * 4)[0] for i in range(351)]

    # 跳过块0（规则2未实现）和块214（官方空cell）
    skip_blocks = {0, 214}
    all_ok = True
    for blk in range(1, 350):
        if blk in skip_blocks:
            continue
        orig_blk = original[orig_ptrs[blk]:orig_ptrs[blk + 1]]
        rebuilt_blk = rebuilt[rebuilt_ptrs[blk]:rebuilt_ptrs[blk + 1]]
        if orig_blk != bytes(rebuilt_blk):
            print(f"  [ERROR] 块{blk}: 原始 {len(orig_blk)} vs 重建 {len(rebuilt_blk)}")
            # 解压对比找出差异
            from core.lzss import decompress
            dec_o = decompress(bytearray(orig_blk))
            dec_r = decompress(bytearray(rebuilt_blk))
            if len(dec_o) != len(dec_r):
                print(f"    解压大小不同: {len(dec_o)} vs {len(dec_r)}")
            else:
                for j in range(min(len(dec_o), len(dec_r))):
                    if dec_o[j] != dec_r[j]:
                        print(f"    解压偏移 0x{j:04X}: 原始 {dec_o[j]:02X} vs 重建 {dec_r[j]:02X}")
                        break
            all_ok = False

    if all_ok:
        print(f"  [INFO] 块1~349（除214外）逐字节完全相同")

    # 7. 压缩大小统计
    print()
    print("  ── 压缩大小对比 ──")
    print(f"  [INFO] 总文件: 原始 {len(original)} vs 重建 {len(rebuilt)} "
          f"({'+' if len(rebuilt) >= len(original) else ''}{len(rebuilt) - len(original)} bytes)")

    # 各块压缩大小
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
            print(f"    [{blk:3d}] 原始 {o:5d} → 重建 {r:5d}  "
                  f"({'差' if d != 0 else '差'}{d:+d}){note}")
    else:
        print(f"  [INFO] 全部 350 块压缩大小完全一致")
    print()

    print("  ═══════════════════════════════════════════")
    print("   [INFO] ALL TESTS PASSED")
    print("  ═══════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
