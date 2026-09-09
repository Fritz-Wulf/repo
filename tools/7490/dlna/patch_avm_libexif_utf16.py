#!/usr/bin/env python3
from pathlib import Path
import hashlib, os, re, stat, subprocess, sys, tempfile

START, END = 0xA930, 0xAA58
ORIG_FULL = "eb39ec2008372fe6f382728fb96201ff4dbd1c48becfc5978e0f27ed3b50677a"
ORIG_SLOT = "b47487188bc06716f6691fd64fe85fd4438b2a2e94a276ed4415aaffe5219487"
BLOB_SHA = "a1a4d4e065ad19e1d659521efe790037ec9d66b6a28fda4035456d4982576a0b"
PATCHED_SLOT = "d9ea47b5af4dc60408f2bd51b3d626d6dc5a7904b7971c0bb34ef32413714ac5"
PATCHED_FULL = "87f82cce704c78c0c11f41aeda1096f944e59cd72a07a23c296a6e7ebb8a0208"
FLAGS = ["-Os", "-mips32r2", "-mabi=32", "-mno-abicalls", "-fno-pic",
         "-fno-stack-protector", "-ffreestanding", "-fno-builtin"]
sha = lambda b: hashlib.sha256(b).hexdigest()

REPO = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name("wulf_utf16_to_utf8.c")

def tool(name):
    roots = []
    if os.environ.get("WULF_TOOLCHAIN_BIN"):
        roots.append(Path(os.environ["WULF_TOOLCHAIN_BIN"]))
    roots.append(REPO / "toolchain/target/bin")
    try:
        common = Path(subprocess.check_output(["git", "-C", str(REPO), "rev-parse", "--path-format=absolute", "--git-common-dir"], text=True).strip())
        roots.append(common.parent / "toolchain/target/bin")
    except (OSError, subprocess.CalledProcessError):
        pass
    for root in roots:
        p = root / name
        if p.is_file() and os.access(p, os.X_OK): return p
    raise RuntimeError(f"target tool missing: {name}")

def build_blob():
    cc, objcopy, readelf = tool("mips-linux-uclibc-gcc"), tool("mips-linux-uclibc-objcopy"), tool("mips-linux-uclibc-readelf")
    with tempfile.TemporaryDirectory() as td:
        obj, raw = Path(td)/"converter.o", Path(td)/"converter.bin"
        subprocess.run([str(cc), *FLAGS, "-c", str(SOURCE), "-o", str(obj)], check=True)
        rel = subprocess.check_output([str(readelf), "-r", str(obj)], text=True)
        if re.search(r"Relocation section .rela?.text", rel): raise RuntimeError("converter text has relocations")
        subprocess.run([str(objcopy), "-O", "binary", "--only-section=.text", str(obj), str(raw)], check=True)
        blob = raw.read_bytes()
    if not blob or len(blob) > END-START or sha(blob) != BLOB_SHA: raise RuntimeError("converter blob mismatch")
    slot = blob + b"\0" * ((END-START)-len(blob))
    if sha(slot) != PATCHED_SLOT: raise RuntimeError("converter slot mismatch")
    return slot

def patch(target):
    target = Path(target)
    before = target.read_bytes(); full = sha(before); slot = sha(before[START:END])
    if full == PATCHED_FULL:
        if slot != PATCHED_SLOT: raise RuntimeError("patched full/slot mismatch")
        return "already-patched"
    if full != ORIG_FULL or slot != ORIG_SLOT: raise RuntimeError("unknown or tampered AVM libexif")
    replacement = build_blob(); after = before[:START] + replacement + before[END:]
    if len(after) != len(before) or sha(after) != PATCHED_FULL: raise RuntimeError("patched image hash mismatch")
    mode = stat.S_IMODE(target.stat().st_mode)
    tmp = target.with_name(target.name + ".wulf-tmp")
    try:
        tmp.write_bytes(after); os.chmod(tmp, mode); os.replace(tmp, target)
    finally:
        if tmp.exists(): tmp.unlink()
    return "patched"

def main(argv):
    if len(argv) != 2: print(f"usage: {argv[0]} LIBEXIF", file=sys.stderr); return 2
    try: state = patch(argv[1])
    except Exception as e: print(f"wulf7490: libexif patch refused: {e}", file=sys.stderr); return 1
    print(f"wulf7490: AVM libexif UTF-16 fix {state}"); return 0

if __name__ == "__main__": raise SystemExit(main(sys.argv))
