"""Step 7b: record the test count from the test files (no number typed by hand)."""

import re
from pathlib import Path

from cairn import record

tests = sorted(Path("tests").glob("test_*.py"))
n = sum(len(re.findall(r"^def test_", p.read_text(), re.M)) for p in tests)
record("tests.n_tests", n, note="count of `def test_` functions in tests/")
record("tests.n_files", len(tests))
