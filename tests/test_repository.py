import json, subprocess, sys, unittest
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

if __name__ == "__main__":
    unittest.main()
