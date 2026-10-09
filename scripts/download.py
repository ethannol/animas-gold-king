"""One-time network step: download the snapshot described by data/raw/query.json.

Deliberately NOT a numbered pipeline step: `cairn run` and `cairn verify` must work
from a fresh checkout without network access. scripts/00_snapshot.py checks the
committed files against data/raw/manifest.json instead.
"""

import argparse
import sys

from animas import acquire

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true", help="recompute checksums only")
    a = ap.parse_args()
    if a.verify:
        sys.exit(0 if all(acquire.verify().values()) else 1)
    acquire.download()
