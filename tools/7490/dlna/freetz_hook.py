#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
META = HERE / "metadata.json"
PATCHER = HERE / "patch_avm_libexif_utf16.py"
TARGET_REL = Path("build/modified/filesystem/lib/libexif.so.12.3.4")
INFO_REL = Path("build/modified/filesystem/etc/freetz_info.cfg")


def fail(message):
    print(f"wulf7490: freetz hook refused: {message}", file=sys.stderr)
    return 1


def parse_exports(path):
    values = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = re.fullmatch(r"export ([A-Z0-9_]+)='([^']*)'", line.strip())
        if match:
            values[match.group(1)] = match.group(2)
    return values


def preflight(root):
    config = root / ".config"
    info_path = root / INFO_REL
    target = root / TARGET_REL
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
    if not target.is_file():
        raise RuntimeError(f"missing target {TARGET_REL}")
    return target, info


def classify_target(target, meta):
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    if digest == meta["original_full_sha256"]:
        return "original", digest
    if digest == meta["patched_full_sha256"]:
        return "already-patched", digest
    raise RuntimeError(f"unknown or tampered AVM libexif: {digest}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Fail-closed Fritz.Wulf 7490 DLNA build hook")
    parser.add_argument("--freetz-root", required=True, type=Path)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args(argv)
    root = args.freetz_root.resolve()
    try:
        target, info = preflight(root)
        meta = json.loads(META.read_text(encoding="utf-8"))
        state, digest = classify_target(target, meta)
        if args.check_only:
            print(f"wulf7490: preflight OK ({state}) {digest}")
            return 0
        if state == "already-patched":
            print("wulf7490: AVM libexif UTF-16 fix already-patched")
            return 0
        env = os.environ.copy()
        toolchain = root / "toolchain/target/bin"
        if "WULF_TOOLCHAIN_BIN" not in env and toolchain.is_dir():
            env["WULF_TOOLCHAIN_BIN"] = str(toolchain)
        proc = subprocess.run([sys.executable, str(PATCHER), str(target)], env=env)
        return proc.returncode
    except Exception as exc:
        return fail(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
