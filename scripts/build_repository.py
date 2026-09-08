#!/usr/bin/env python3
from pathlib import Path
import gzip, hashlib, json

root = Path(__file__).resolve().parents[1]

catalog = []
for p in sorted((root / "metadata/packages").glob("*.json")) if (root / "metadata/packages").is_dir() else []:
    data = json.loads(p.read_text(encoding="utf-8"))
    catalog.extend(data if isinstance(data, list) else [data])
catalog.sort(key=lambda x: (x["name"], x["version"]))

stanzas = []
for pkg in catalog:
    stanza = [
        f'Package: {pkg["name"]}',
        f'Version: {pkg["version"]}',
        f'Architecture: {pkg["architecture"]}',
        f'Description: {pkg["description"]}',
        f'Filename: {pkg["download"]}',
        f'Size: {pkg["size"]}',
        f'SHA256sum: {pkg["sha256"]}',
        f'Source: {pkg["source_ref"]}',
        f'X-Fritz-Wulf-Platform: {pkg["platform"]}',
        f'X-Fritz-Wulf-Compatibility: {pkg["compatibility"]}',
        f'X-Fritz-Wulf-Installable: {"yes" if pkg.get("installable", True) else "no"}',
    ]
    if pkg.get("depends"):
        stanza.insert(3, "Depends: " + ", ".join(pkg["depends"]))
    stanzas.append("\n".join(stanza))
packages = root / "Packages"
packages.write_text("\n\n".join(stanzas) + ("\n" if stanzas else ""), encoding="utf-8")
with gzip.GzipFile(filename=str(root / "Packages.gz"), mode="wb", mtime=0) as fh:
    fh.write(packages.read_bytes())

idx_path = root / "index.json"
idx = json.loads(idx_path.read_text(encoding="utf-8"))
idx["architectures"] = sorted({p["architecture"] for p in catalog})
idx["packages"] = catalog
idx_path.write_text(json.dumps(idx, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

include = ["index.json", "Packages", "Packages.gz"]
include += [str(p.relative_to(root)) for p in sorted((root / "devices").glob("*/device.json"))]
include += [p["download"] for p in catalog]
lines = []
for rel in include:
    p = root / rel
    lines.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {rel}")
(root / "SHA256SUMS").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"built repository metadata for {len(catalog)} packages and {len(include)} checksummed files")
