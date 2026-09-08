#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, subprocess, sys

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "metadata/upstream/yourfritz-history.json").read_text(encoding="utf-8"))
gitdir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/home/andreas/src/yourfritz-import.git")
out_root = root / "packages/sources/yourfritz"
catalog = []

for comp in manifest["components"]:
    package = comp["package"]
    for item in comp["versions"]:
        version = item["version"]
        source_path = item["source_path"]
        blob = subprocess.check_output(
            ["git", f"--git-dir={gitdir}", "show", f'{item["source_commit"]}:{source_path}']
        )
        digest = hashlib.sha256(blob).hexdigest()
        if digest != item["sha256"]:
            raise SystemExit(f"hash mismatch for {package} {version}: {digest}")
        target = out_root / package / version / Path(source_path).name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(blob)
        rel = target.relative_to(root).as_posix()
        catalog.append({
            "name": f"yourfritz-{package}",
            "version": version,
            "architecture": "all",
            "platform": "source-snapshot",
            "depends": [],
            "description": f"Historical YourFritz source snapshot: {package}",
            "download": rel,
            "size": len(blob),
            "sha256": digest,
            "source_ref": f'PeterPawn/YourFritz@{item["source_commit"]}:{source_path}',
            "compatibility": "historical-source-only",
            "installable": False,
            "upstream_date": item["date"],
            "upstream_subject": item["subject"],
            "license": manifest["license"],
        })

catalog.sort(key=lambda p: (p["name"], p["version"]))
metadata_dir = root / "metadata/packages"
metadata_dir.mkdir(parents=True, exist_ok=True)
(metadata_dir / "yourfritz-source.json").write_text(
    json.dumps(catalog, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
)
print(f"materialized {len(catalog)} YourFritz historical source snapshots")
