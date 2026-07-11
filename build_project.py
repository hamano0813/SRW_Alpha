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
        print(f"[OK] Compiled: {module_prefix}.pyd")
    else:
        print(f"[OK] Compiled: {os.path.basename(src_pyd)}")

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

    print(f"[OK] Deployed to {src_dir}/")
    return True


def build_lzss():
    print("=" * 60)
    print("  Building LZSS native extension...")
    print("=" * 60)
    return _build_extension(
        src_dir=os.path.join(PROJECT_ROOT, "src", "core", "lzss"),
        module_prefix="_lzss",
    )


def main():
    print()
    print("  Super Robot Wars Alpha ROM Editor - Build Script")
    print()

    all_ok = True

    print()
    ok = build_lzss()
    if ok:
        print("[DONE]   LZSS native extension")
    else:
        print("[FAILED] LZSS native extension")
        all_ok = False
    print()

    if all_ok:
        print("=" * 60)
        print("  Build completed successfully!")
        print("=" * 60)
        print()
        print("  Available imports:")
        print("    from core.lzss import compress, decompress")
        print()
        return 0
    else:
        print("=" * 60)
        print("  Build completed with errors!")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
