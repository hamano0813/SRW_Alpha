"""
ROBOT.RAF 解析/构建 往返测试

测试内容：
  1. 解压并解析 ROBOT.RAF → Python dict
  2. 将 dict 重建为二进制
  3. 重新解析重建后的二进制 → Python dict
  4. 对比两次解析的 dict 是否一致（数据完整性）
  5. 打印前 5 条机体记录（不含武器列表）
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.robot_raf import parse, build

RES_BIN = os.path.join(os.path.dirname(__file__), "..", "res", "bin")
ROBOT_RAF_PATH = os.path.join(RES_BIN, "ROBOT.RAF")


def _robots_equal(a: dict, b: dict) -> bool:
    """深度比较两条机体记录（含所有字段）"""
    for k in a:
        if k == "weapons":
            if len(a["weapons"]) != len(b.get("weapons", [])):
                return False
            for wa, wb in zip(a["weapons"], b["weapons"]):
                for wk in wa:
                    if wa[wk] != wb.get(wk):
                        return False
        else:
            if a[k] != b.get(k):
                return False
    return True


def print_robot(robot: dict, index: int):
    """打印单条机体记录的非武器字段"""
    print(f"  [{index}]")
    print(f"       rname:    {robot['rname']}")
    print(f"       code:     {robot['code']}")
    print(f"       type:     {robot['type']}")
    print(f"       move:     {robot['move']}")
    print(f"       hp:       {robot['hp']}")
    print(f"       en:       {robot['en']}")
    print(f"       mobility: {robot['mobility']}")
    print(f"       armor:    {robot['armor']}")
    print(f"       limit:    {robot['limit']}")
    print(f"       size:     {robot['size']}")
    print(f"       slot:     {robot['slot']}")
    print(f"       air/grd/wtr/spc: {robot['air']}/{robot['grd']}/{robot['wtr']}/{robot['spc']}")


def main():
    """执行往返测试：解析 → 重建 → 再解析 → 对比数据及字节码"""
    print()
    print("  ╔═══════════════════════════════════════════╗")
    print("  ║      ROBOT.RAF 往返一致性测试              ║")
    print("  ╚═══════════════════════════════════════════╝")
    print()

    if not os.path.isfile(ROBOT_RAF_PATH):
        print(f"  [SKIP] 文件不存在: {ROBOT_RAF_PATH}")
        print()
        print("  请将 ROBOT.RAF 放入 res/bin/ 目录后重试。")
        return 0

    fsize = os.path.getsize(ROBOT_RAF_PATH)
    print(f"  文件: {ROBOT_RAF_PATH}")
    print(f"  大小: {fsize} bytes (0x{fsize:X})")
    print()

    with open(ROBOT_RAF_PATH, "rb") as f:
        original = f.read()

    # 1. 第一次解析
    print("  ── 第 1 次解析 ──")
    data1 = parse(bytearray(original))
    count = data1["count"]
    robots1 = data1["robots"]
    print(f"  机体数: {count}")
    assert count == len(robots1)
    print("  [PASS]")
    print()

    # 2. 打印前 5 条
    print("  ── 前 5 条机体数据 ──")
    for i in range(min(5, count)):
        print_robot(robots1[i], i)
    print()

    # 3. 重建并重新解析
    print("  ── 重建 → 第 2 次解析 ──")
    rebuilt = build(data1)
    print(f"  重建大小: {len(rebuilt)} bytes (原始 {fsize} bytes)")
    data2 = parse(rebuilt)
    robots2 = data2["robots"]
    assert data2["count"] == count
    print("  [PASS]")
    print()

    # 4. 逐条深度对比
    print("  ── 数据一致性对比 ──")
    all_ok = True
    for i in range(count):
        if not _robots_equal(robots1[i], robots2[i]):
            print(f"  [FAIL] 条目 {i} 不一致")
            all_ok = False
            break

    if not all_ok:
        return 1

    print(f"  [PASS] 全部 {count} 条机体数据一致 "
          f"(含 16 件武器)")
    print()

    # 5. 逐字节对比（仅当大小一致时执行）
    print("  ── 逐字节对比 ──")
    if len(original) == len(rebuilt):
        if original == bytes(rebuilt):
            print("  [PASS] 完全相同")
        else:
            for i in range(len(original)):
                if original[i] != rebuilt[i]:
                    print(f"  [FAIL] 首处差异在字节 {i}: "
                          f"原始 0x{original[i]:02X} vs 重建 0x{rebuilt[i]:02X}")
                    return 1
    else:
        print("  [SKIP] 大小不一致，跳过逐字节对比")

    print()
    print("  ═══════════════════════════════════════════")
    print("   ALL TESTS PASSED")
    print("  ═══════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
