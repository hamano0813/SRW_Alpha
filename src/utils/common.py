"""
通用工具函数模块

提供应用程序重启、字体信息提取、系统字体映射等实用功能。
支持 TTF、OTF、TTC 等多种字体格式的处理。

Functions:
    restart: 重启当前应用程序
    get_font_info: 提取字体的系列名称
    get_font_mapping: 获取系统字体映射
"""

import os
import sys
from concurrent.futures import ThreadPoolExecutor

from fontTools.ttLib import TTCollection, TTFont


def restart():
    """重启当前应用程序"""
    exe = sys.executable
    argv = [exe] + sys.argv
    os.execv(exe, argv)


def get_font_info(font_obj: TTFont | str, langID=1033) -> str:
    """
    提取字体的系列名称

    从字体文件或字体对象中提取指定语言的字体系列名称。
    支持 TTF、OTF、TTC 格式，优先使用指定语言，失败时回退到默认语言。

    Args:
        font_obj: 字体文件路径或 TTFont 对象
        langID: 语言 ID，默认 1033（英语），中文可用 0x804/0x404/0x411

    Returns:
        str: 字体系列名称，失败时返回空字符串
    """
    if isinstance(font_obj, str):
        ext = os.path.splitext(font_obj)[1].lower()
        if ext in (".ttf", ".otf"):
            font_obj = TTFont(font_obj)
        elif ext == ".ttc":
            ttc = TTCollection(font_obj)
            if not ttc.fonts:
                return ""
            font_obj = ttc.fonts[0]
        else:
            return ""

    if "name" not in font_obj:
        return ""

    for record in font_obj["name"].names:  # type: ignore
        # platformID=3(Microsoft), nameID=1(Font Family name)
        if record.platformID == 3 and record.langID == langID and record.nameID == 1:
            try:
                return record.toUnicode()
            except (UnicodeDecodeError, AttributeError):
                continue

    return ""


def _process_font_file(font_file: str, fonts_dir: str) -> tuple[str, str] | None:
    """
    处理单个字体文件并返回字体系列名到文件路径的映射。

    Args:
        font_file: 字体文件名
        fonts_dir: 字体目录路径

    Returns:
        tuple[str, str] | None: (字体系列名, 文件路径) 或 None（处理失败时）
    """
    ext = os.path.splitext(font_file)[1].lower()
    if ext not in (".ttf", ".otf", ".ttc"):
        return None

    font_path = os.path.join(fonts_dir, font_file)
    if not os.path.isfile(font_path):
        return None

    try:
        if ext == ".ttc":
            ttc = TTCollection(font_path)
            if ttc.fonts:
                family = get_font_info(ttc.fonts[0])
                if family:
                    return (family, font_path)
        else:
            ttf = TTFont(font_path)
            family = get_font_info(ttf)
            if family:
                return (family, font_path)
    except Exception:
        pass

    return None


def get_font_mapping() -> dict[str, str]:
    """
    获取系统字体映射

    扫描 Windows 系统字体目录，建立字体系列名称到文件路径的映射关系。
    使用多线程并行处理以提高扫描效率。

    Returns:
        dict[str, str]: 字体系列名称到文件路径的映射字典
    """
    fonts_dir = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
    if not os.path.isdir(fonts_dir):
        return {}

    font_mapping = {}
    font_files = os.listdir(fonts_dir)

    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(lambda font_file: _process_font_file(font_file, fonts_dir), font_files)
        for result in results:
            if result:
                family, font_path = result
                font_mapping[family] = font_path

    return font_mapping
