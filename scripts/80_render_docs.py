"""Step 8: render the README, walkthrough and resume bullet from their templates with the
ledger, so every number in them is a recorded value. Fails on any unresolved key."""

from pathlib import Path

from cairn import load_ledger, render

ROOT = Path(__file__).resolve().parents[1]
ledger = load_ledger()
pairs = [("README.tmpl.md", "README.md"), ("docs/walkthrough.tmpl.md", "docs/walkthrough.md"),
         ("docs/resume_bullet.tmpl.md", "docs/resume_bullet.md")]
for src, dst in pairs:
    text, missing = render((ROOT / src).read_text(), ledger)
    if missing:
        raise SystemExit(f"{src}: unresolved ledger keys {sorted(set(missing))}")
    (ROOT / dst).write_text(text)
    print(f"rendered {dst} from {src}")
