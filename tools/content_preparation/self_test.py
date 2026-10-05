"""Run the bounded content preparation test suite without training datasets."""
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))


def main():
    suite=unittest.defaultTestLoader.discover(str(ROOT/"tests"/"content_preparation"))
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() and not result.skipped else 1


if __name__=="__main__":
    raise SystemExit(main())
