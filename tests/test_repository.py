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

if __name__ == "__main__":
    unittest.main()
