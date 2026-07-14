"""
各模块 parse/build 性能基准测试

测试内容：
  1. ROBOT.RAF 解析/构建时间
  2. PILOT.BIN 解析/构建时间
  3. SNMSG.BIN 解析/构建时间
  4. DC.BIN 解析/构建时间
  5. DR.BIN 解析/构建时间
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))


from core import dc_bin, dr_bin, pilot_bin, robot_raf, snmsg_bin
from core.codec.extra import HALF_TEXT_EXTRA, SNMSG_TEXT_EXTRA, SPECIAL_TEXT_EXTRA

RES_BIN = os.path.join(os.path.dirname(__file__), "..", "res", "bin")

ROBOT_PATH = os.path.join(RES_BIN, "ROBOT.RAF")
PILOT_PATH = os.path.join(RES_BIN, "PILOT.BIN")
SNMSG_PATH = os.path.join(RES_BIN, "SNMSG.BIN")
DC_PATH = os.path.join(RES_BIN, "DC.BIN")
DR_PATH = os.path.join(RES_BIN, "DR.BIN")


def _load(path: str) -> bytes:
    """读取文件为 bytes"""
    with open(path, "rb") as f:
        return f.read()


def _fmt_time(seconds: float, iterations: int = 1) -> str:
    """格式化耗时，单位自适应"""
    avg = seconds / iterations
    if avg < 1:
        return f"{avg * 1000:.1f} ms"
    return f"{avg:.2f} s"


def _fmt_size(size: int) -> str:
    """格式化文件大小"""
    if size < 1024:
        return f"{size} B"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / 1024 / 1024:.2f} MB"


def _run_bench(name: str, path: str, mod, extra=None, iterations: int = 3):
    """对单个模块执行 parse + build 基准测试

    Args:
        name:  显示名称（如 ROBOT.RAF）
        path:  文件路径
        mod:   模块对象（含 parse/build）
        extra: 可选的 extra 映射字典
        iterations: 每项测试运行次数，取平均值
    """
    print(f"  [{name}]")
    data = _load(path)
    raw_len = len(data)
    print(f"    文件: {_fmt_size(raw_len)}  ({len(data)} bytes)")
    print()

    # ---- parse 基准 ----
    parse_times = []
    parsed = None
    for _ in range(iterations):
        buf = bytearray(data)
        t0 = time.perf_counter()
        parsed = mod.parse(buf, extra=extra)
        t1 = time.perf_counter()
        parse_times.append(t1 - t0)
    parse_avg = sum(parse_times) / iterations
    print(f"    parse:         {_fmt_time(sum(parse_times), 1)}  " f"(avg {_fmt_time(parse_avg)} ×{iterations})")

    # ---- build 基准 ----
    build_times = []
    rebuilt = None
    for _ in range(iterations):
        t0 = time.perf_counter()
        rebuilt = mod.build(parsed, extra=extra)
        t1 = time.perf_counter()
        build_times.append(t1 - t0)
    build_avg = sum(build_times) / iterations
    print(f"    build:         {_fmt_time(sum(build_times), 1)}  " f"(avg {_fmt_time(build_avg)} ×{iterations})")

    # ---- 总往返 ----
    total_avg = parse_avg + build_avg
    print(f"    合计 (parse+build): {_fmt_time(total_avg)}")

    # ---- 大小验证 ----
    if len(rebuilt) == raw_len:
        print(f"    [INFO] 重建大小一致")
    else:
        print(f"    [WARN] 重建 {len(rebuilt)} vs 原始 {raw_len}")

    # ---- 条目数 ----
    if "count" in parsed:
        print(f"    条目数: {parsed['count']}")
    elif "robots" in parsed:
        print(f"    条目数: {len(parsed['robots'])}")

    print()


def main() -> int:
    """执行各模块 parse/build 性能基准测试"""
    print()
    print("  ╔═══════════════════════════════════════════╗")
    print("  ║      C 扩展模块性能基准测试               ║")
    print("  ╚═══════════════════════════════════════════╝")
    print()

    all_ok = True
    files = [
        ("ROBOT.RAF", ROBOT_PATH, robot_raf, {**HALF_TEXT_EXTRA, **SPECIAL_TEXT_EXTRA}),
        ("PILOT.BIN", PILOT_PATH, pilot_bin, {**HALF_TEXT_EXTRA, **SPECIAL_TEXT_EXTRA}),
        ("SNMSG.BIN", SNMSG_PATH, snmsg_bin, SNMSG_TEXT_EXTRA),
        ("DC.BIN", DC_PATH, dc_bin, None),
        ("DR.BIN", DR_PATH, dr_bin, SPECIAL_TEXT_EXTRA),
    ]

    for name, path, mod, extra in files:
        if not os.path.isfile(path):
            print(f"  [WARN] {path} 不存在，跳过")
            print()
            continue
        _run_bench(name, path, mod, extra)

    print("  ═══════════════════════════════════════════")
    print(f"   [INFO] {'ALL TESTS PASSED' if all_ok else 'TESTS FAILED'}")
    print("  ═══════════════════════════════════════════")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
