"""
项目构建脚本

编译 C 扩展并执行其他构建任务。
新任务请在此文件中按顺序添加。
"""

import glob
import os
import shutil
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def _build_extension(src_dir: str, module_prefix: str) -> bool:
    """编译 C 扩展并保持产物在源码目录。

    Args:
        src_dir:  源码目录（含 setup.py 和 .c 文件）
        module_prefix:  模块文件名前缀

    Returns:
        成功返回 True
    """
    if not os.path.isdir(src_dir):
        print(f"[ERROR] Source directory not found: {src_dir}")
        return False

    result = subprocess.run(
        [sys.executable, "setup.py", "build_ext", "--inplace"],
        cwd=src_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if result.returncode != 0:
        print("[ERROR] Compilation failed:")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return False

    pyd_files = glob.glob(os.path.join(src_dir, f"{module_prefix}*.pyd"))
    if not pyd_files:
        print("[ERROR] Compiled .pyd file not found!")
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return False

    src_pyd = pyd_files[0]
    dst_pyd = os.path.join(src_dir, f"{module_prefix}.pyd")

    if src_pyd != dst_pyd:
        if os.path.exists(dst_pyd):
            os.remove(dst_pyd)
        os.rename(src_pyd, dst_pyd)
        print(f"[INFO] Compiled: {module_prefix}.pyd")
    else:
        print(f"[INFO] Compiled: {os.path.basename(src_pyd)}")

    build_dir = os.path.join(src_dir, "build")
    if os.path.isdir(build_dir):
        shutil.rmtree(build_dir)
        print("  -> Cleaned up build/ directory")

    for pattern in ("*.pyc", "__pycache__"):
        for found in glob.glob(os.path.join(src_dir, "**", pattern), recursive=True):
            if os.path.isfile(found):
                os.remove(found)
            elif os.path.isdir(found):
                shutil.rmtree(found)

    print(f"[INFO] Deployed to {src_dir}/")
    return True


def build_lzss():
    print("=" * 60)
    print("  Building LZSS native extension...")
    print("=" * 60)
    return _build_extension(
        src_dir=os.path.join(PROJECT_ROOT, "src", "core", "lzss"),
        module_prefix="_lzss",
    )


def build_robot_raf():
    print("=" * 60)
    print("  Building ROBOT.RAF native extension...")
    print("=" * 60)
    return _build_extension(
        src_dir=os.path.join(PROJECT_ROOT, "src", "core", "robot_raf"),
        module_prefix="_robot_raf",
    )


def build_pilot_bin():
    print("=" * 60)
    print("  Building PILOT.BIN native extension...")
    print("=" * 60)
    return _build_extension(
        src_dir=os.path.join(PROJECT_ROOT, "src", "core", "pilot_bin"),
        module_prefix="_pilot_bin",
    )


def build_snmsg_bin():
    print("=" * 60)
    print("  Building SNMSG.BIN native extension...")
    print("=" * 60)
    return _build_extension(
        src_dir=os.path.join(PROJECT_ROOT, "src", "core", "snmsg_bin"),
        module_prefix="_snmsg_bin",
    )


def build_dc_bin():
    print("=" * 60)
    print("  Building DC.BIN native extension...")
    print("=" * 60)
    return _build_extension(
        src_dir=os.path.join(PROJECT_ROOT, "src", "core", "dc_bin"),
        module_prefix="_dc_bin",
    )


def build_dr_bin():
    print("=" * 60)
    print("  Building DR.BIN native extension...")
    print("=" * 60)
    return _build_extension(
        src_dir=os.path.join(PROJECT_ROOT, "src", "core", "dr_bin"),
        module_prefix="_dr_bin",
    )


def build_sndata():
    print("=" * 60)
    print("  Building SNDATA.BIN native extension...")
    print("=" * 60)
    return _build_extension(
        src_dir=os.path.join(PROJECT_ROOT, "src", "core", "sndata_bin"),
        module_prefix="_sndata",
    )


def build_codec():
    print("=" * 60)
    print("  Building codec native extension...")
    print("=" * 60)
    return _build_extension(
        src_dir=os.path.join(PROJECT_ROOT, "src", "core", "codec"),
        module_prefix="_codec",
    )


def main():
    print()
    print("  Super Robot Wars Alpha ROM Editor - Build Script")
    print()

    all_ok = True

    print()
    ok = build_lzss()
    if ok:
        print("[INFO]   LZSS native extension")
    else:
        print("[ERROR] LZSS native extension")
        all_ok = False

    print()
    ok = build_robot_raf()
    if ok:
        print("[INFO]   ROBOT.RAF native extension")
    else:
        print("[ERROR] ROBOT.RAF native extension")
        all_ok = False

    print()
    ok = build_pilot_bin()
    if ok:
        print("[INFO]   PILOT.BIN native extension")
    else:
        print("[ERROR] PILOT.BIN native extension")
        all_ok = False

    print()
    ok = build_snmsg_bin()
    if ok:
        print("[INFO]   SNMSG.BIN native extension")
    else:
        print("[ERROR] SNMSG.BIN native extension")
        all_ok = False

    print()
    ok = build_dc_bin()
    if ok:
        print("[INFO]   DC.BIN native extension")
    else:
        print("[ERROR] DC.BIN native extension")
        all_ok = False

    print()
    ok = build_dr_bin()
    if ok:
        print("[INFO]   DR.BIN native extension")
    else:
        print("[ERROR] DR.BIN native extension")
        all_ok = False

    print()
    ok = build_sndata()
    if ok:
        print("[INFO]   SNDATA.BIN native extension")
    else:
        print("[ERROR] SNDATA.BIN native extension")
        all_ok = False

    print()
    ok = build_codec()
    if ok:
        print("[INFO]   codec native extension")
    else:
        print("[ERROR] codec native extension")
        all_ok = False
    print()

    if all_ok:
        print("=" * 60)
        print("  Build completed successfully!")
        print("=" * 60)
        print()
        print("  Available imports:")
        print("    import core.lzss as lzss")
        print("    import core.robot_raf as robot_raf")
        print("    import core.pilot_bin as pilot_bin")
        print("    import core.snmsg_bin as snmsg_bin")
        print("    import core.dc_bin as dc_bin")
        print("    import core.dr_bin as dr_bin")
        print("    import core.sndata_bin as sndata_bin")
        print("    import core.codec as codec")
        print()
        return 0
    else:
        print("=" * 60)
        print("  Build completed with errors!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
