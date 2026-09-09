#!/usr/bin/env python3
import argparse
from pathlib import Path
import shutil
import sys

from freetz_hook import INFO_REL, parse_exports

HERE = Path(__file__).resolve().parent
FILES = (
    "freetz_hook.py",
    "patch_avm_libexif_utf16.py",
    "wulf_utf16_to_utf8.c",
    "metadata.json",
)
MARKER = "FRITZWULF_7490_DLNA_UTF16"
HOOK = '''    # FRITZWULF_7490_DLNA_UTF16\n    python3 "$(dirname "$0")/custom/wulf7490/freetz_hook.py" --freetz-root "$(dirname "$0")" || return 1\n'''


def validate_tree(root):
    config = root / ".config"
    info_path = root / INFO_REL
    fwmod = root / "fwmod_custom"
    if not config.is_file():
        raise RuntimeError("missing Freetz .config")
    if "FREETZ_TYPE_7490=y" not in config.read_text(encoding="utf-8", errors="replace").splitlines():
        raise RuntimeError("requires FREETZ_TYPE_7490=y")
    if not info_path.is_file():
        raise RuntimeError(f"missing {INFO_REL}")
    info = parse_exports(info_path)
    if info.get("FREETZ_INFO_BOXTYPE") != "7490":
        raise RuntimeError("freetz_info box type is not 7490")
    if info.get("FREETZ_INFO_FIRMWAREVERSION") != "07.62":
        raise RuntimeError("requires FRITZ!OS 07.62")
    if not fwmod.is_file():
        raise RuntimeError("missing fwmod_custom")
    return fwmod


def stage(root):
    fwmod = validate_tree(root)
    dest = root / "custom/wulf7490"
    dest.mkdir(parents=True, exist_ok=True)
    if any(dest.glob("libexif.so*")):
        raise RuntimeError("vendor libexif must not be staged in custom/wulf7490")
    for name in FILES:
        shutil.copy2(HERE / name, dest / name)
    text = fwmod.read_text(encoding="utf-8")
    if MARKER not in text:
        anchor = "all() {\n"
        if anchor not in text:
            raise RuntimeError("fwmod_custom all() hook anchor not found")
        text = text.replace(anchor, anchor + HOOK, 1)
        fwmod.write_text(text, encoding="utf-8")
    return dest


def main(argv=None):
    parser = argparse.ArgumentParser(description="Stage Fritz.Wulf 7490 DLNA sources into a Freetz tree")
    parser.add_argument("--freetz-root", required=True, type=Path)
    parser.add_argument("--apply", action="store_true", help="write files and patch fwmod_custom")
    args = parser.parse_args(argv)
    root = args.freetz_root.resolve()
    try:
        validate_tree(root)
        if not args.apply:
            print(f"wulf7490: stage plan OK for {root}")
            return 0
        dest = stage(root)
        print(f"wulf7490: staged DLNA build hook in {dest}")
        return 0
    except Exception as exc:
        print(f"wulf7490: staging refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
