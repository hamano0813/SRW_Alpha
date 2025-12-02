import os
import sys
from concurrent.futures import ThreadPoolExecutor

from fontTools.ttLib import TTCollection, TTFont


def restart():
    exe = sys.executable
    argv = [exe] + sys.argv
    os.execv(exe, argv)


def get_font_info(font_obj: TTFont | str, langID=1033) -> str:
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
        if record.platformID == 3 and record.langID == langID and record.nameID == 1:
            try:
                return record.toUnicode()
            except (UnicodeDecodeError, AttributeError):
                continue

    return ""


def _process_font_file(font_file: str, fonts_dir: str) -> tuple[str, str] | None:
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
