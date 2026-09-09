#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
import re
import urllib.request
from pathlib import Path

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
TAG_RE = re.compile(r"^v([0-9]+(?:\.[0-9]+){2}(?:[-+][0-9A-Za-z.-]+)?)$")
CORE_FIELDS = ("download", "size", "sha256", "source_ref", "source_commit")


def version_key(version):
    main, _, suffix = version.partition("-")
    nums = tuple(int(part) for part in main.split("."))
    return nums, (1 if not suffix else 0), suffix


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def release_asset(release, version):
    wanted = f"fw-{version}.tar.gz"
    matches = [asset for asset in release.get("assets", []) if asset.get("name") == wanted]
    if len(matches) != 1:
        raise ValueError(f"release v{version} must contain exactly one {wanted} asset")
    asset = matches[0]
    digest = str(asset.get("digest") or "")
    if not digest.startswith("sha256:") or not SHA256_RE.fullmatch(digest[7:]):
        raise ValueError(f"release v{version} has no valid GitHub sha256 digest")
    if int(asset.get("size") or 0) <= 0:
        raise ValueError(f"release v{version} has invalid asset size")
    if not asset.get("browser_download_url"):
        raise ValueError(f"release v{version} has no download URL")
    return asset, digest[7:]


def entry_for_release(release, version, asset, digest, commit):
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError(f"release v{version} did not resolve to a commit SHA")
    return {
        "name": "fw",
        "version": version,
        "architecture": "all",
        "platform": "fritzwulf-package-manager",
        "depends": [],
        "description": release.get("name") or f"Fritz.Wulf package manager {version}",
        "download": f"packages/fritzwulf/fw/{version}/{asset['name']}",
        "size": int(asset["size"]),
        "sha256": digest,
        "source_ref": f"Fritz-Wulf/fw@v{version}",
        "source_commit": commit,
        "compatibility": "cross-generation-client-foundation",
        "devices": ["3270", "7490", "7530", "7590"],
        "installable": False,
        "release_date": release.get("published_at"),
        "channel": "testing" if release.get("prerelease") else "stable",
        "verification": "VERIFIED",
    }


def verify_payload(version, asset, digest, payload):
    if len(payload) != int(asset["size"]):
        raise ValueError(f"release v{version} asset size mismatch")
    actual = sha256_bytes(payload)
    if actual != digest:
        raise ValueError(f"release v{version} asset checksum mismatch")


def materialize(version, asset, digest, packages_root, fetch_asset):
    target = packages_root / version / asset["name"]
    if target.exists():
        verify_payload(version, asset, digest, target.read_bytes())
        return target
    payload = fetch_asset(asset["browser_download_url"])
    verify_payload(version, asset, digest, payload)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    temporary.write_bytes(payload)
    temporary.replace(target)
    return target


def sync_releases(releases, existing, packages_root, fetch_asset, resolve_commit):
    by_version = {item["version"]: item for item in existing if item.get("name") == "fw"}
    if len(by_version) != len(existing):
        raise ValueError("fw metadata must contain only fw package entries")
    for release in releases:
        if release.get("draft"):
            continue
        match = TAG_RE.fullmatch(str(release.get("tag_name") or ""))
        if not match:
            continue
        version = match.group(1)
        asset, digest = release_asset(release, version)
        commit = resolve_commit(release["tag_name"])
        candidate = entry_for_release(release, version, asset, digest, commit)
        old = by_version.get(version)
        if old is not None:
            for field in CORE_FIELDS:
                if old.get(field) != candidate.get(field):
                    raise ValueError(
                        f"release v{version} conflicts with existing metadata: {field}"
                    )
        materialize(version, asset, digest, packages_root, fetch_asset)
        if old is None:
            by_version[version] = candidate
    return [by_version[key] for key in sorted(by_version, key=version_key)]


def request_bytes(url, token=None):
    headers = {"User-Agent": "Fritz.Wulf-repository-sync"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def request_json(url, token=None):
    return json.loads(request_bytes(url, token).decode("utf-8"))


def github_releases(repository, token=None):
    releases = []
    for page in range(1, 101):
        url = f"https://api.github.com/repos/{repository}/releases?per_page=100&page={page}"
        batch = request_json(url, token)
        if not isinstance(batch, list):
            raise ValueError("GitHub releases API did not return a list")
        releases.extend(batch)
        if len(batch) < 100:
            break
    else:
        raise ValueError("release pagination exceeded safety limit")
    return releases


def github_commit_resolver(repository, token=None):
    def resolve(tag):
        url = f"https://api.github.com/repos/{repository}/commits/{tag}"
        data = request_json(url, token)
        sha = str(data.get("sha") or "")
        if not re.fullmatch(r"[0-9a-f]{40}", sha):
            raise ValueError(f"cannot resolve {tag} to commit")
        return sha
    return resolve


def main():
    parser = argparse.ArgumentParser(description="Sync Fritz-Wulf/fw releases into the repository")
    parser.add_argument("--repository", default="Fritz-Wulf/fw")
    parser.add_argument("--releases-json", type=Path)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    metadata_path = root / "metadata/packages/fw.json"
    packages_root = root / "packages/fritzwulf/fw"
    existing = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else []
    token = os.environ.get("GITHUB_TOKEN")
    if args.releases_json:
        releases = json.loads(args.releases_json.read_text(encoding="utf-8"))
    else:
        releases = github_releases(args.repository, token)
    entries = sync_releases(
        releases=releases,
        existing=existing,
        packages_root=packages_root,
        fetch_asset=lambda url: request_bytes(url, token),
        resolve_commit=github_commit_resolver(args.repository, token),
    )
    rendered = json.dumps(entries, indent=2, ensure_ascii=False) + "\n"
    if not metadata_path.exists() or metadata_path.read_text(encoding="utf-8") != rendered:
        metadata_path.write_text(rendered, encoding="utf-8")
    print(f"fw release sync: {len(entries)} versions")


if __name__ == "__main__":
    main()
