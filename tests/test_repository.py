import subprocess
import sys
import unittest

class RepositoryTest(unittest.TestCase):
    def test_repository_validator(self):
        subprocess.run([sys.executable,'scripts/build_repository.py'],check=True)
        subprocess.run([sys.executable,'scripts/validate_repository.py'],check=True)

if __name__ == '__main__':
    unittest.main()
