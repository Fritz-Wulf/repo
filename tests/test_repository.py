import ctypes, hashlib, json, re, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class RepositoryTest(unittest.TestCase):
    def test_build_is_reproducible_and_valid(self):
        subprocess.run([sys.executable, "scripts/build_repository.py"], cwd=ROOT, check=True)
        first = (ROOT / "Packages.gz").read_bytes()
        subprocess.run([sys.executable, "scripts/build_repository.py"], cwd=ROOT, check=True)
        self.assertEqual(first, (ROOT / "Packages.gz").read_bytes())
        subprocess.run([sys.executable, "scripts/validate_repository.py"], cwd=ROOT, check=True)
        idx = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
        keys = [(p["name"], p["version"], p["architecture"]) for p in idx["packages"]]
        self.assertEqual(len(keys), len(set(keys)))

    def test_fw_release_is_catalogued(self):
        subprocess.run([sys.executable, "scripts/build_repository.py"], cwd=ROOT, check=True)
        idx = json.loads((ROOT / "index.json").read_text(encoding="utf-8"))
        fw = [p for p in idx["packages"] if p["name"] == "fw" and p["version"] == "0.1.0"]
        self.assertEqual(len(fw), 1)
        self.assertEqual(fw[0]["source_ref"], "Fritz-Wulf/fw@v0.1.0")
        self.assertEqual(fw[0]["sha256"], "968e09eff06b0f63663663e51248623a8ef2bcf8bfbb18f36a415169943fc5bf")
        versions = sorted(p["version"] for p in idx["packages"] if p["name"] == "fw")
        self.assertEqual(versions, ["0.1.0", "0.1.1", "0.2.0", "0.2.1", "0.3.0"])

    def test_7490_utf16_converter_vectors(self):
        source = (ROOT / "tools/7490/dlna/wulf_utf16_to_utf8.c").read_text()
        portable = re.sub(r"static __inline__ unsigned read_le16.*?\n}\n\n", "static unsigned read_le16(const unsigned char *p) { return (unsigned)p[0] | ((unsigned)p[1] << 8); }\n\n", source, count=1, flags=re.S)
        with tempfile.TemporaryDirectory() as td:
            cfile, sofile = Path(td)/"converter.c", Path(td)/"converter.so"
            cfile.write_text(portable)
            subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(cfile), "-o", str(sofile)], check=True)
            fn = ctypes.CDLL(str(sofile)).wulf_utf16_to_utf8
            fn.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint]
            for text in ["ASCII", "ÄÖÜ ß é", "日本語", "😀"]:
                raw = text.encode("utf-16le") + b"\0\0"; out = ctypes.create_string_buffer(128)
                fn(out, ctypes.create_string_buffer(raw), len(out)); self.assertEqual(out.value.decode(), text)
            for raw in [b"\x00\xd8\x00\x00", b"\x00\xdc\x00\x00"]:
                out = ctypes.create_string_buffer(16); fn(out, ctypes.create_string_buffer(raw), len(out)); self.assertEqual(out.value.decode(), "�")
            out = ctypes.create_string_buffer(4); raw = "😀".encode("utf-16le") + b"\0\0"
            fn(out, ctypes.create_string_buffer(raw), len(out)); self.assertEqual(out.value, b"")

    def test_7490_stager_is_idempotent_and_vendor_free(self):
        stager = ROOT / "tools/7490/dlna/stage_into_freetz.py"
        with tempfile.TemporaryDirectory() as td:
            tree = Path(td); (tree / ".config").write_text("FREETZ_TYPE_7490=y\n")
            info = tree / "build/modified/filesystem/etc/freetz_info.cfg"; info.parent.mkdir(parents=True)
            info.write_text("export FREETZ_INFO_BOXTYPE='7490'\nexport FREETZ_INFO_FIRMWAREVERSION='07.62'\n")
            (tree / "fwmod_custom").write_text("#!/usr/bin/env bash\nall() {\n    :\n}\n")
            for _ in range(2):
                proc = subprocess.run([sys.executable, str(stager), "--freetz-root", str(tree), "--apply"], text=True, capture_output=True)
                self.assertEqual(proc.returncode, 0, proc.stderr)
            hook = (tree / "fwmod_custom").read_text(); self.assertEqual(hook.count("FRITZWULF_7490_DLNA_UTF16"), 1)
            staged = tree / "custom/wulf7490"
            for name in ["freetz_hook.py", "patch_avm_libexif_utf16.py", "wulf_utf16_to_utf8.c", "metadata.json"]:
                self.assertTrue((staged / name).is_file())
            self.assertFalse(any(p.name == "libexif.so.12.3.4" for p in staged.rglob("*")))

    def test_7490_freetz_hook_fails_closed_on_profile_and_target(self):
        hook = ROOT / "tools/7490/dlna/freetz_hook.py"
        with tempfile.TemporaryDirectory() as td:
            tree = Path(td)
            info = tree / "build/modified/filesystem/etc/freetz_info.cfg"
            target = tree / "build/modified/filesystem/lib/libexif.so.12.3.4"
            info.parent.mkdir(parents=True); target.parent.mkdir(parents=True)
            info.write_text("export FREETZ_INFO_BOXTYPE='7490'\nexport FREETZ_INFO_FIRMWAREVERSION='07.62'\n")
            target.write_bytes(b"not-a-known-avm-library")
            (tree / ".config").write_text("# CONFIG_FREETZ_TYPE_7490 is not set\n")
            bad_profile = subprocess.run([sys.executable, str(hook), "--freetz-root", str(tree), "--check-only"], text=True, capture_output=True)
            self.assertEqual(bad_profile.returncode, 1); self.assertIn("FREETZ_TYPE_7490=y", bad_profile.stderr)
            (tree / ".config").write_text("FREETZ_TYPE_7490=y\n")
            unknown = subprocess.run([sys.executable, str(hook), "--freetz-root", str(tree), "--check-only"], text=True, capture_output=True)
            self.assertEqual(unknown.returncode, 1); self.assertIn("unknown or tampered", unknown.stderr)

    def test_7490_dlna_patch_sources_are_reconstructed(self):
        meta = json.loads((ROOT / "tools/7490/dlna/metadata.json").read_text())
        self.assertEqual(meta["verification"], "HISTORICAL VERIFIED")
        self.assertFalse(meta["redistributes_vendor_binary"])
        patcher = ROOT / "tools/7490/dlna/patch_avm_libexif_utf16.py"
        source = ROOT / "tools/7490/dlna/wulf_utf16_to_utf8.c"
        self.assertEqual(hashlib.sha256(patcher.read_bytes()).hexdigest(), meta["patcher_sha256"])
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), meta["converter_source_sha256"])
        text = patcher.read_text()
        for digest in (meta["original_full_sha256"], meta["original_slot_sha256"], meta["generated_blob_sha256"], meta["patched_slot_sha256"], meta["patched_full_sha256"]):
            self.assertIn(digest, text)

    def test_3270_historical_build_evidence_is_preserved(self):
        profile = json.loads((ROOT / "devices/3270/device.json").read_text())
        hist = profile["historical_build"]
        self.assertEqual(hist["verification"], "HISTORICAL VERIFIED")
        self.assertEqual(hist["variant"], "FRITZ!Box WLAN 3270 v3")
        self.assertEqual(hist["fritzos"], "05.54")
        self.assertEqual(hist["freetz_version"], "freetz-ng-766MF-acc1f895ff")
        self.assertFalse(hist["flash_boot_verified"])
        self.assertRegex(hist["busybox_sha256"], r"^[0-9a-f]{64}$")

    def test_7490_profile_is_historical_not_unbounded_verified(self):
        profile = json.loads((ROOT / "devices/7490/device.json").read_text())
        self.assertEqual(profile["verification"], "HISTORICAL VERIFIED")
        self.assertEqual(profile["fritzos_versions"], ["07.62"])
        self.assertIn("historical", profile["flash_support"].lower())

    def test_generation_profiles_are_evidence_backed(self):
        expected = {
            "3270": ("mips32", "little", "ur8"),
            "7530": ("armv7", "little", "ipq40xx"),
            "7590": ("mips32", "big", "grx5"),
        }
        for model, (arch, endian, soc) in expected.items():
            profile = json.loads((ROOT / "devices" / model / "device.json").read_text())
            self.assertEqual(profile["verification"], "INFERRED")
            self.assertEqual(profile["architecture"], arch)
            self.assertEqual(profile["endianness"], endian)
            self.assertEqual(profile["soc_family"].lower(), soc)
            self.assertTrue(profile["package_architecture"])
            self.assertGreaterEqual(len(profile["evidence"]), 2)
            for item in profile["evidence"]:
                self.assertTrue(item["url"].startswith("https://"))
                self.assertIn(item["verification"], {"VERIFIED", "INFERRED"})

    def test_neonwulf_catalog_contract(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        css = (ROOT / "assets/css/neonwulf.css").read_text(encoding="utf-8")
        self.assertIn('assets/css/neonwulf.css', html)
        self.assertIn('assets/js/catalog-app.mjs', html)
        self.assertIn('id="package-search"', html)
        self.assertIn('aria-label="Paketliste"', html)
        self.assertIn('data-sort="name"', html)
        self.assertIn('prefers-reduced-motion', css)
        self.assertIn('focus-visible', css)

    def test_fw_release_sync_workflow_is_pr_gated(self):
        workflow = (ROOT / ".github/workflows/sync-fw-releases.yml").read_text(encoding="utf-8")
        self.assertIn("schedule:", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("contents: write", workflow)
        self.assertIn("pull-requests: write", workflow)
        self.assertIn("scripts/sync_fw_releases.py", workflow)
        self.assertIn("scripts/build_repository.py", workflow)
        self.assertIn("scripts/validate_repository.py", workflow)
        self.assertIn("gh pr create", workflow)
        self.assertNotIn("git push origin main", workflow)

if __name__ == "__main__":
    unittest.main()
