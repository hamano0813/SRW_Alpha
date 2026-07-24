"""
SRW_Alpha 一键发布脚本

整合 C 扩展编译 → Python 编译 → 资源打包 → 安装程序生成。

用法:
    cd 项目根目录
    python build/build_release.py

依赖（构建工具需提前安装）:
    - Python 3.14+
    - uv
    - BatToExeConverter (C:\\Softwares\\Bat2Exe\\)
    - Inno Setup (C:\\Softwares\\Inno Setup\\)
"""

import glob
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
SCRIPT_DIR = DIST_DIR / "script"

# ======================== C 扩展配置 ========================
C_EXTENSIONS = [
    {"dir": "src/core/lzss",      "module": "_lzss"},
    {"dir": "src/core/codec",     "module": "_codec"},
    {"dir": "src/core/dc_bin",    "module": "_dc_bin"},
    {"dir": "src/core/dr_bin",    "module": "_dr_bin"},
    {"dir": "src/core/pilot_bin", "module": "_pilot_bin"},
    {"dir": "src/core/robot_raf", "module": "_robot_raf"},
    {"dir": "src/core/sndata_bin","module": "_sndata"},
    {"dir": "src/core/snmsg_bin", "module": "_snmsg_bin"},
]

# ======================== Python 源码目录 ========================
SRC_PACKAGES = [
    "core",
    "gui",
    "utils",
]

# ======================== 额外资源 ========================
ASSETS = ["tools"]


# ======================== 日志与工具 ========================

def banner(title: str) -> None:
    """打印分区标题"""
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def step(num: str, title: str) -> None:
    """打印步骤标题"""
    print(f"\n\033[1m[STEP {num}] {title}\033[0m")


def log(msg: str) -> None:
    """打印信息"""
    print(f"  [INFO] {msg}")


def ok(msg: str) -> None:
    """打印成功"""
    print(f"  [INFO] {msg}")


def warn(msg: str) -> None:
    """打印警告"""
    print(f"  [WARN] {msg}")


def error(msg: str) -> None:
    """打印错误并退出"""
    print(f"  [ERROR] {msg}")
    sys.exit(1)


def run(cmd, cwd=None, check=True) -> subprocess.CompletedProcess:
    """执行命令并捕获输出"""
    result = subprocess.run(
        cmd, cwd=cwd,
        capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    if result.returncode != 0 and check:
        print(f"  [ERROR] Command failed: {' '.join(str(c) for c in cmd)}")
        if result.stdout:
            for line in result.stdout.splitlines():
                print(f"    | {line}")
        if result.stderr:
            for line in result.stderr.splitlines():
                print(f"    | {line}")
        sys.exit(1)
    return result


def find_version() -> str:
    """从 pyproject.toml 读取版本号"""
    pyproject = PROJECT_ROOT / "pyproject.toml"
    if pyproject.exists():
        text = pyproject.read_text(encoding="utf-8")
        m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
        if m:
            return m.group(1)
    return "0.0.0"


# ======================== STEP 1: 清理 ========================

def step_clean():
    """清理 dist 目录"""
    step("1/8", "清理构建目录")

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    SCRIPT_DIR.mkdir(parents=True)
    ok("dist/ 已清理")


# ======================== STEP 2: UV 工具链 ========================

def step_uv():
    """升级 uv、升级依赖、复制工具链"""
    step("2/8", "准备 UV 工具链与依赖升级")

    log("升级 uv...")
    run(["uv", "self", "update"], check=False)

    log("升级项目依赖到最新兼容版本...")
    run(["uv", "lock", "--upgrade"])
    ok("依赖升级完成")

    uv_files = ["uv.exe", "uvx.exe", "uvw.exe"]
    local_bin = Path(os.environ["USERPROFILE"]) / ".local" / "bin"
    for f in uv_files:
        src = local_bin / f
        if src.exists():
            shutil.copy2(src, DIST_DIR / f)
            ok(f"{f}")

    # uv 镜像配置
    shutil.copy2(BUILD_DIR / "uv.toml", DIST_DIR / "uv.toml")
    ok("uv.toml")

    # Python 版本锁定
    py_ver = PROJECT_ROOT / ".python-version"
    if py_ver.exists():
        shutil.copy2(py_ver, DIST_DIR / ".python-version")

    # pyproject
    shutil.copy2(PROJECT_ROOT / "pyproject.toml", DIST_DIR / "pyproject.toml")

    # uv.lock（若无则锁定）
    uv_lock = PROJECT_ROOT / "uv.lock"
    if uv_lock.exists():
        shutil.copy2(uv_lock, DIST_DIR / "uv.lock")


# ======================== STEP 3: C 扩展 ========================

def step_c_extensions():
    """编译所有 C 扩展"""
    step("3/8", "编译 C 扩展")

    for ext in C_EXTENSIONS:
        ext_dir = PROJECT_ROOT / ext["dir"]
        module = ext["module"]
        print(f"\n  ── {module} ──")

        if not ext_dir.exists():
            warn(f"目录不存在: {ext_dir}")
            continue

        result = subprocess.run(
            [sys.executable, "setup.py", "build_ext", "--inplace"],
            cwd=str(ext_dir),
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )

        if result.returncode != 0:
            error(f"{module} 编译失败: {result.stderr or result.stdout}")

        # 查找 .pyd 文件（可能有 cp314-win_amd64 等后缀）
        pyd_files = list(ext_dir.glob(f"{module}*.pyd"))
        if not pyd_files:
            error(f"未找到 {module}*.pyd")

        src_pyd = pyd_files[0]
        dst_pyd = ext_dir / f"{module}.pyd"

        if src_pyd != dst_pyd:
            if dst_pyd.exists():
                dst_pyd.unlink()
            src_pyd.rename(dst_pyd)

        ok(f"{module}.pyd")

        # 清理临时文件
        build_dir = ext_dir / "build"
        if build_dir.exists():
            shutil.rmtree(build_dir)

        for pyc in ext_dir.rglob("*.pyc"):
            pyc.unlink()
        for cache in ext_dir.rglob("__pycache__"):
            shutil.rmtree(cache)


# ======================== STEP 4: Python 编译 ========================

def step_python_compile():
    """将 Python 源码编译为 .pyc，复制 .pyd"""
    step("4/8", "编译 Python 源码")
    import py_compile

    # src/ 下顶层文件（main.py, config.py, res.py）
    src_root = PROJECT_ROOT / "src"
    top_files = ["main.py", "config.py", "res.py"]
    for f in top_files:
        py_file = src_root / f
        if py_file.exists():
            pyc_target = SCRIPT_DIR / py_file.relative_to(src_root)
            pyc_target = pyc_target.with_suffix(".pyc")
            pyc_target.parent.mkdir(parents=True, exist_ok=True)
            py_compile.compile(str(py_file), cfile=str(pyc_target), doraise=True)
            ok(f"{f} → .pyc")

    # 各包目录
    for pkg in SRC_PACKAGES:
        pkg_dir = src_root / pkg
        if not pkg_dir.exists():
            warn(f"跳过不存在的包: {pkg}")
            continue

        for py_file in sorted(pkg_dir.rglob("*.py")):
            if py_file.name == "setup.py":
                continue
            if "build" in py_file.parts or "__pycache__" in py_file.parts:
                continue

            rel = py_file.relative_to(src_root)
            pyc_target = SCRIPT_DIR / rel.with_suffix(".pyc")
            pyc_target.parent.mkdir(parents=True, exist_ok=True)

            try:
                py_compile.compile(str(py_file), cfile=str(pyc_target), doraise=True)
            except py_compile.PyCompileError as e:
                error(f"编译失败: {rel} — {e}")

    # 复制 .pyd 到对应目录
    for pyd_file in sorted(src_root.rglob("*.pyd")):
        if "build" in pyd_file.parts or "__pycache__" in pyd_file.parts:
            continue
        rel = pyd_file.relative_to(src_root)
        target = SCRIPT_DIR / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(pyd_file, target)
        ok(f"{rel}")

    log(f"Python 编译完成 → {SCRIPT_DIR}")


# ======================== STEP 5: 复制额外资源 ========================

def step_assets():
    """复制 tools/ 等额外资源"""
    step("5/8", "复制额外资源")

    for asset in ASSETS:
        src = PROJECT_ROOT / asset
        dst = DIST_DIR / asset
        if not src.exists():
            warn(f"跳过不存在的资源: {asset}")
            continue
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        ok(f"{asset}")

    # 卸载辅助脚本（PowerShell GUI 弹窗）
    ps1 = BUILD_DIR / "uninstall_helper.ps1"
    if ps1.exists():
        shutil.copy2(ps1, DIST_DIR / "uninstall_helper.ps1")
        ok("uninstall_helper.ps1")

    # 从 PATH 查找 UPX
    upx = shutil.which("upx.exe")
    if upx:
        shutil.copy2(upx, DIST_DIR / "upx.exe")
        # 查找配套的 man 文件
        upx_dir = Path(upx).parent
        upx_man = upx_dir / "upx.1"
        if upx_man.exists():
            shutil.copy2(upx_man, DIST_DIR / "upx.1")
        ok("upx.exe (自 PATH)")
    else:
        warn("UPX 未找到，跳过压缩工具复制（install.bat 中的 UPX 步骤将被跳过）")


# ======================== STEP 6: 生成 EXE 入口 ========================

def step_entry_point():
    """将 main.bat 编译为 SRW_Alpha.exe"""
    step("6/8", "生成程序入口")

    bat_tool = r"C:\Softwares\Bat2Exe\BatToExeConverter.exe"
    if not os.path.exists(bat_tool):
        warn("BatToExeConverter 未找到，跳过 exe 生成")
        return

    version = find_version()
    icon_path = PROJECT_ROOT / "res" / "icon.ico"

    # 复制 main.bat 到 dist/
    shutil.copy2(BUILD_DIR / "main.bat", DIST_DIR / "main.bat")

    cmd = [
        bat_tool,
        "/bat", str(BUILD_DIR / "main.bat"),
        "/exe", str(DIST_DIR / "SRW_Alpha.exe"),
        "/invisible",
        "/productname", "Super Robot Wars Alpha ROM Editor",
        "/description", "超级机器人大战α ROM 编辑器",
        "/internalname", "SRW_Alpha",
        "/fileversion", f"{version}.0",
        "/productversion", f"{version}.0",
        "/copyright", "Copyright © 2025",
    ]
    if icon_path.exists():
        cmd.extend(["/icon", str(icon_path)])

    run(cmd)
    ok(f"SRW_Alpha.exe (v{version})")


# ======================== STEP 7: 生成安装程序 ========================

def step_installer():
    """调用 ISCC 生成 Inno Setup 安装程序"""
    step("7/8", "生成安装程序")

    iscc = r"C:\Softwares\Inno Setup\ISCC.exe"
    if not os.path.exists(iscc):
        warn("ISCC 未找到，跳过安装程序生成")
        return

    # 复制 setup.iss 到 dist/
    iss_src = BUILD_DIR / "setup.iss"
    if iss_src.exists():
        shutil.copy2(iss_src, DIST_DIR / "setup.iss")

    run([iscc, "/Qp", str(DIST_DIR / "setup.iss")], cwd=str(DIST_DIR))
    ok("安装程序生成完成")


# ======================== STEP 8: 生成 ZIP 压缩包 ========================

def step_zip():
    """将安装程序打包为 zip"""
    step("8/8", "生成 ZIP 压缩包")

    version = find_version()
    exe_name = f"SRW_Alpha-{version}-x64.exe"
    zip_name = f"SRW_Alpha-{version}-x64.zip"

    exe_path = DIST_DIR / exe_name
    if not exe_path.exists():
        warn(f"安装程序未找到: {exe_name}")
        return

    import zipfile
    with zipfile.ZipFile(PROJECT_ROOT / zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(exe_path, arcname=exe_name)

    ok(f"{zip_name}")


# ======================== 主流程 ========================

def main() -> int:
    """执行全部构建步骤"""
    version = find_version()

    print()
    banner(f"SRW Alpha ROM Editor v{version} — 发布包构建")
    print(f"  项目根目录: {PROJECT_ROOT}")

    step_clean()
    step_uv()
    step_c_extensions()
    step_python_compile()
    step_assets()
    step_entry_point()
    step_installer()
    step_zip()

    print()
    banner("构建完成！")
    print(f"  dist/:  {DIST_DIR}")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
