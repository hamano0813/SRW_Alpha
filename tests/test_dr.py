"""
DR.BIN 解析/构建 往返测试

测试内容：
  1. 解析 DR.BIN → Python dict
  2. 验证名册与机体数据完整性
  3. 重建为二进制并重新解析
  4. 对比数据一致性
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from core.dr_bin import build, parse
from core.codec.extra import HALF_TEXT_EXTRA

RES_BIN = os.path.join(os.path.dirname(__file__), "..", "res", "bin")
DR_PATH = os.path.join(RES_BIN, "DR.BIN")


def main() -> int:
    """执行往返测试"""
    print("  [DR.BIN] Parse/Build roundtrip")

    if not os.path.isfile(DR_PATH):
        print(f"  [WARN] missing: {DR_PATH}")
        return 0

    fsize = os.path.getsize(DR_PATH)
    print(f"  [INFO] size = {fsize} bytes")

    with open(DR_PATH, "rb") as f:
        original = f.read()

    # ===== Parse with HALF_TEXT_EXTRA (for proper text display) =====
    data1 = parse(original, extra=HALF_TEXT_EXTRA)
    roster = data1["roster"]
    dr_list = data1["dr"]
    count = data1["count"]

    assert len(roster) == 448
    assert len(dr_list) == 448
    assert count == 448

    assert roster[0] == "ヒュッケバインMK-II"
    assert roster[1] == "ヒュッケバインMK-III"
    assert roster[2] == "ヒュッケバインボクサー"
    print("  [INFO] roster[0..2] OK")

    r0 = dr_list[0]
    assert r0["name"] == "ヒュッケバインMK-II"
    assert r0["height"] == "20.8m"
    assert r0["weight"] == "52.0t"
    assert r0["appr"] == "オリジナル"
    assert r0["flags"] == 0x15
    assert len(r0["desc"]) > 0
    print("  [INFO] robot[0] fields OK")

    # ===== Build without extra（避免 HALF_TEXT_EXTRA 映射损失）=----
    # 用无 extra 的原始数据做往返，确保数据一致性
    data_raw = parse(original)
    rebuilt = build(data_raw)
    print(f"  [INFO] rebuilt {len(rebuilt)} / original {fsize} bytes")

    data2 = parse(rebuilt)
    assert data2["count"] == count

    all_ok = True
    for i in range(count):
        for key in ("name", "height", "weight", "appr", "flags", "desc"):
            if data_raw["dr"][i][key] != data2["dr"][i][key]:
                print(f"  [ERROR] dr[{i}].{key} mismatch")
                all_ok = False

    for i in range(len(roster)):
        if data_raw["roster"][i] != data2["roster"][i]:
            print(f"  [ERROR] roster[{i}] mismatch")
            all_ok = False

    if all_ok:
        print(f"  [INFO] all {count} entries consistent")

    print(f"  {'[INFO] ALL TESTS PASSED' if all_ok else '[ERROR] TESTS FAILED'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
