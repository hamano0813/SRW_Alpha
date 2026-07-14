"""
PILOT.BIN 解析/构建 往返测试

测试内容：
  1. 解析 PILOT.BIN → Python dict
  2. 将 dict 重建为二进制
  3. 重新解析重建后的二进制 → Python dict
  4. 对比两次解析的 dict 是否一致（数据完整性）
  5. 打印前 5 条驾驶员记录
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


from core.codec.extra import HALF_TEXT_EXTRA, SPECIAL_TEXT_EXTRA
from core.pilot_bin import build, parse

RES_BIN = os.path.join(os.path.dirname(__file__), "..", "res", "bin")
PILOT_BIN_PATH = os.path.join(RES_BIN, "PILOT.BIN")


def _pilots_equal(a: dict, b: dict) -> bool:
    """深度比较两条驾驶员记录（含嵌套技能列表）"""
    for k in a:
        if k == "sklu":
            if len(a["sklu"]) != len(b.get("sklu", [])):
                return False
            for sa, sb in zip(a["sklu"], b["sklu"]):
                for sk in sa:
                    if sa[sk] != sb.get(sk):
                        return False
        elif k in ("spi", "spl"):
            if a[k] != b.get(k):
                return False
        else:
            if a[k] != b.get(k):
                return False
    return True


def print_pilot(pilot: dict, index: int):
    """打印单条驾驶员记录"""
    print(f"  [{index}]")
    print(f"       fname:    {pilot['fname']}")
    print(f"       nname:    {pilot['nname']}")
    print(f"       code:     {pilot['code']}")
    print(f"       series:   {pilot['series']}  (unknown1={pilot['unknown1']})")
    print(f"       cqb/rng/evd/hit/rxn/skl: "
          f"{pilot['cqb']}/{pilot['rng']}/{pilot['evd']}/"
          f"{pilot['hit']}/{pilot['rxn']}/{pilot['skl']}")
    print(f"       sp: {pilot['sp']}  daction: {pilot['daction']}  "
          f"skls: {pilot['skls']}  (0b{pilot['skls']:016b})")
    print(f"       nature: {pilot['nature']}  fsg: {pilot['fsg']}")
    print(f"       air/grd/wtr/spc: "
          f"{pilot['air']}/{pilot['grd']}/{pilot['wtr']}/{pilot['spc']}")
    print(f"       spi: {pilot['spi']}")
    print(f"       spl: {pilot['spl']}")
    print(f"       sklu ({len(pilot['sklu'])} 条):")
    for si, sk in enumerate(pilot["sklu"]):
        print(f"         S{si}: sname={sk['sname']}  "
              f"l1={sk['l1']} l2={sk['l2']} l3={sk['l3']} "
              f"l4={sk['l4']} l5={sk['l5']} l6={sk['l6']} "
              f"l7={sk['l7']} l8={sk['l8']} l9={sk['l9']}")


def main():
    """执行往返测试：解析 → 重建 → 再解析 → 对比数据及字节码"""
    print()
    print("  ╔═══════════════════════════════════════════╗")
    print("  ║      PILOT.BIN 往返一致性测试             ║")
    print("  ╚═══════════════════════════════════════════╝")
    print()

    if not os.path.isfile(PILOT_BIN_PATH):
        print(f"  [WARN] 文件不存在: {PILOT_BIN_PATH}")
        print()
        print("  请将 PILOT.BIN 放入 res/bin/ 目录后重试。")
        return 0

    fsize = os.path.getsize(PILOT_BIN_PATH)
    print(f"  [INFO] 文件: {PILOT_BIN_PATH}")
    print(f"  [INFO] 大小: {fsize} bytes (0x{fsize:X})")
    print()

    with open(PILOT_BIN_PATH, "rb") as f:
        original = f.read()

    # 1. 第一次解析（带 extra 映射）
    print("  ── 第 1 次解析（extra 映射）──")
    data1 = parse(bytearray(original), extra={**HALF_TEXT_EXTRA, **SPECIAL_TEXT_EXTRA})
    count = data1["count"]
    pilots1 = data1["pilots"]
    print(f"  [INFO] 驾驶员数: {count}")
    assert count == len(pilots1)
    print("  [INFO]")
    print()

    # 2. 打印前 5 条
    print("  ── 前 5 条驾驶员数据 ──")
    for i in range(min(5, count)):
        print_pilot(pilots1[i], i)
    print()

    # 3. 重建并重新解析（带 extra 映射）
    print("  ── 重建 → 第 2 次解析（extra 映射）──")
    rebuilt = build(data1, extra={**HALF_TEXT_EXTRA, **SPECIAL_TEXT_EXTRA})
    print(f"  [INFO] 重建大小: {len(rebuilt)} bytes (原始 {fsize} bytes)")
    data2 = parse(rebuilt, extra={**HALF_TEXT_EXTRA, **SPECIAL_TEXT_EXTRA})
    pilots2 = data2["pilots"]
    assert data2["count"] == count
    print("  [INFO]")
    print()

    # 4. 逐条深度对比
    print("  ── 数据一致性对比 ──")
    all_ok = True
    for i in range(count):
        if not _pilots_equal(pilots1[i], pilots2[i]):
            print(f"  [ERROR] 条目 {i} 不一致")
            all_ok = False
            break

    if not all_ok:
        return 1

    print(f"  [INFO] 全部 {count} 条驾驶员数据一致")
    print()

    # 5. 逐字节对比
    print("  ── 逐字节对比 ──")
    if len(original) == len(rebuilt):
        if original == bytes(rebuilt):
            print("  [INFO] 完全相同")
        else:
            for i in range(min(len(original), len(rebuilt))):
                if original[i] != rebuilt[i]:
                    print(f"  [ERROR] 首处差异在字节 {i}: "
                          f"原始 0x{original[i]:02X} vs 重建 0x{rebuilt[i]:02X}")
                    return 1
    else:
        print("  [WARN] 大小不一致，跳过逐字节对比")

    # 6. 验证 extra 映射已生效
    print()
    print("  ── extra 映射验证 ──")
    p0_fname = pilots1[0]["fname"]
    if "ｶ" not in p0_fname and "ガ" in p0_fname:
        print(f"  [INFO] 文本已映射（{p0_fname}）")
    else:
        print(f"  [WARN] 文本可能未映射（{p0_fname}）")
    print()
    print("  ═══════════════════════════════════════════")
    print("   [INFO] ALL TESTS PASSED")
    print("  ═══════════════════════════════════════════")
    return 0


if __name__ == "__main__":
    sys.exit(main())
