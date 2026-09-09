import hashlib
import tempfile
import unittest
from pathlib import Path

from scripts.sync_fw_releases import sync_releases


class FwReleaseSyncTest(unittest.TestCase):
    def setUp(self):
        self.payload = b"fritz-wulf-fw-release\n"
        self.digest = hashlib.sha256(self.payload).hexdigest()
        self.release = {
            "tag_name": "v9.9.9",
            "name": "fw v9.9.9",
            "published_at": "2026-09-09T03:00:00Z",
            "html_url": "https://github.com/Fritz-Wulf/fw/releases/tag/v9.9.9",
            "assets": [{
                "name": "fw-9.9.9.tar.gz",
                "size": len(self.payload),
                "digest": f"sha256:{self.digest}",
                "browser_download_url": "https://example.invalid/fw-9.9.9.tar.gz",
            }],
        }

    def run_sync(self, existing=None):
        root = Path(tempfile.mkdtemp())
        entries = sync_releases(
            releases=[self.release],
            existing=existing or [],
            packages_root=root,
            fetch_asset=lambda _url: self.payload,
            resolve_commit=lambda _tag: "a" * 40,
        )
        return entries, root
    def test_new_release_is_materialized_with_verified_metadata(self):
        entries, root = self.run_sync()
        self.assertEqual([p["version"] for p in entries], ["9.9.9"])
        pkg = entries[0]
        self.assertEqual(pkg["sha256"], self.digest)
        self.assertEqual(pkg["source_commit"], "a" * 40)
        self.assertFalse(pkg["installable"])
        artifact = root / "9.9.9" / "fw-9.9.9.tar.gz"
        self.assertEqual(artifact.read_bytes(), self.payload)

    def test_missing_github_digest_is_rejected(self):
        self.release["assets"][0]["digest"] = None
        with self.assertRaisesRegex(ValueError, "sha256 digest"):
            self.run_sync()

    def test_wrong_download_bytes_are_rejected(self):
        root = Path(tempfile.mkdtemp())
        with self.assertRaisesRegex(ValueError, "checksum"):
            sync_releases(
                [self.release], [], root,
                fetch_asset=lambda _url: b"x" * len(self.payload),
                resolve_commit=lambda _tag: "a" * 40,
            )
    def test_existing_history_is_preserved(self):
        existing = [{
            "name": "fw", "version": "0.1.0", "architecture": "all",
            "platform": "fritzwulf-package-manager", "depends": [],
            "description": "old", "download": "packages/fritzwulf/fw/0.1.0/fw-0.1.0.tar.gz",
            "size": 1, "sha256": "b" * 64, "source_ref": "Fritz-Wulf/fw@v0.1.0",
            "source_commit": "c" * 40, "compatibility": "cross-generation-client-foundation",
            "installable": False, "release_date": "2026-01-01T00:00:00Z",
            "channel": "stable", "verification": "VERIFIED",
        }]
        entries, _ = self.run_sync(existing)
        self.assertEqual([p["version"] for p in entries], ["0.1.0", "9.9.9"])
        self.assertEqual(entries[0], existing[0])

    def test_conflicting_existing_release_fails_closed(self):
        entries, _ = self.run_sync()
        conflicting = [dict(entries[0], sha256="0" * 64)]
        with self.assertRaisesRegex(ValueError, "conflicts with existing metadata"):
            self.run_sync(conflicting)



    def test_new_fw_release_targets_all_supported_devices(self):
        entries, _ = self.run_sync()
        self.assertEqual(
            entries[0]["devices"],
            ["3270", "7490", "7530", "7590"],
        )

if __name__ == "__main__":
    unittest.main()
