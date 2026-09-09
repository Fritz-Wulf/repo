#!/usr/bin/env python3
from pathlib import Path
import gzip, hashlib, json, re, sys

root = Path(__file__).resolve().parents[1]
errors = []
idx = json.loads((root / "index.json").read_text(encoding="utf-8"))
if idx.get("format_version") != 1:
    errors.append("unsupported index format")

for model in idx.get("devices", []):
    p = root / "devices" / model / "device.json"
    if not p.is_file():
        errors.append(f"missing device profile: {model}")
    else:
        d = json.loads(p.read_text(encoding="utf-8"))
        if d.get("verification") not in {"VERIFIED", "HISTORICAL VERIFIED", "INFERRED", "UNKNOWN"}:
            errors.append(f"invalid verification: {model}")
        if d.get("verification") == "INFERRED":
            evidence = d.get("evidence", [])
            if not evidence:
                errors.append(f"inferred profile missing evidence: {model}")
            for item in evidence:
                if not str(item.get("url", "")).startswith("https://"):
                    errors.append(f"invalid evidence URL: {model}")
                if item.get("verification") not in {"VERIFIED", "INFERRED"}:
                    errors.append(f"invalid evidence verification: {model}")

seen = set()
for pkg in idx.get("packages", []):
    key = (pkg.get("name"), pkg.get("version"), pkg.get("architecture"))
    if key in seen:
        errors.append(f"duplicate package version: {key}")
    seen.add(key)
    for field in ("name","version","architecture","platform","description","download","size","sha256","source_ref","compatibility","devices"):
        if field not in pkg:
            errors.append(f"package missing {field}: {key}")
    devices = pkg.get("devices")
    if not isinstance(devices, list):
        errors.append(f"package devices must be a list: {key}")
    else:
        if len(devices) != len(set(devices)):
            errors.append(f"duplicate package device target: {key}")
        unknown = sorted(set(devices) - set(idx.get("devices", [])))
        if unknown:
            errors.append(f"unknown package device target {unknown}: {key}")
    rel = pkg.get("download", "")
    if rel.startswith("/") or ".." in Path(rel).parts:
        errors.append(f"unsafe package path: {rel}")
        continue
    p = root / rel
    if not p.is_file():
        errors.append(f"missing package file: {rel}")
        continue
    if p.stat().st_size != pkg.get("size"):
        errors.append(f"package size mismatch: {rel}")
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    if digest != pkg.get("sha256"):
        errors.append(f"package checksum mismatch: {rel}")
    if not re.fullmatch(r"[0-9a-f]{64}", str(pkg.get("sha256", ""))):
        errors.append(f"invalid package sha256: {rel}")

with gzip.open(root / "Packages.gz", "rb") as fh:
    if fh.read() != (root / "Packages").read_bytes():
        errors.append("Packages.gz mismatch")

checksum_paths = set()
for line in (root / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
    digest, rel = line.split("  ", 1)
    checksum_paths.add(rel)
    p = root / rel
    if not p.is_file():
        errors.append(f"missing checksummed file: {rel}")
    elif hashlib.sha256(p.read_bytes()).hexdigest() != digest:
        errors.append(f"checksum mismatch: {rel}")
for pkg in idx.get("packages", []):
    if pkg["download"] not in checksum_paths:
        errors.append(f"package missing from SHA256SUMS: {pkg['download']}")

if errors:
    print("\n".join("ERROR: " + e for e in errors))
    sys.exit(1)
print(f"repository validation: OK ({len(idx.get('packages', []))} packages)")
