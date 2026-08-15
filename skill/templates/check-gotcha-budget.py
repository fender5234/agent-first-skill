#!/usr/bin/env python3
"""Enforces the gotcha budget: at most N added to EXISTING blocks per commit.

The manifest is not a changelog. Gotchas earn their place by being footguns a
future agent would otherwise hit — a manifest that collects every observation
stops being read, which costs more than the notes were worth.

The rule existed as prose ("budget: 1-2 per session") and was violated the first
time it met a busy session: five added in one run. It is machine-checkable, so it
should not have been prose.

**New blocks are exempt.** A block added in this same commit documents its own
footguns as part of describing itself; that is not manifest spam. Only growth of
blocks that already existed counts against the budget — that is where padding
accumulates.

Usage:
    python documentation/check-gotcha-budget.py          # budget 2
    python documentation/check-gotcha-budget.py 3        # custom budget

Exit 0 within budget, 1 over. Safe in a pre-commit hook.
"""
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pyyaml not installed. Run: pip install pyyaml")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
DOCS = ROOT / "documentation"
DEFAULT_BUDGET = 2


def git(*args: str) -> tuple[str, int]:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return r.stdout, r.returncode


def gotcha_counts(text: str) -> dict[str, int]:
    """{block_name: number_of_gotchas} for one manifest's contents."""
    try:
        data = yaml.safe_load(text) or {}
    except yaml.YAMLError:
        return {}
    blocks = data.get("blocks") or {}
    if not isinstance(blocks, dict):
        return {}
    counts = {}
    for name, block in blocks.items():
        if not isinstance(block, dict):
            continue
        g = block.get("gotchas") or []
        counts[name] = len(g) if isinstance(g, list) else 0
    return counts


def main(argv: list[str]) -> int:
    budget = int(argv[0]) if argv and argv[0].isdigit() else DEFAULT_BUDGET

    staged, _ = git("diff", "--cached", "--name-only")
    manifests = [
        f for f in staged.splitlines()
        if f.startswith("documentation/") and f.endswith(".yaml")
    ]
    if not manifests:
        return 0

    added_existing: list[tuple[str, str, int]] = []  # file, block, delta
    added_new: list[tuple[str, str, int]] = []

    for path in manifests:
        head_text, code = git("show", f"HEAD:{path}")
        before = gotcha_counts(head_text) if code == 0 else {}
        after_path = ROOT / path
        if not after_path.exists():
            continue
        after = gotcha_counts(after_path.read_text(encoding="utf-8"))

        for block, count in after.items():
            if block not in before:
                if count:
                    added_new.append((path, block, count))
            else:
                delta = count - before[block]
                if delta > 0:
                    added_existing.append((path, block, delta))

    total = sum(d for _, _, d in added_existing)

    if added_new:
        shown = ", ".join(f"{b} (+{d})" for _, b, d in added_new)
        print(f"note: {sum(d for _,_,d in added_new)} gotchas on NEW blocks, exempt: {shown}")

    if total <= budget:
        if total:
            print(f"OK: {total} gotcha(s) added to existing blocks, budget {budget}")
        return 0

    print(f"Gotcha budget exceeded: {total} added to existing blocks, budget is {budget}.")
    for path, block, delta in added_existing:
        print(f"  {path}: {block} +{delta}")
    print()
    print("The manifest is not a changelog. Keep the ones a future agent would")
    print("otherwise trip over; drop the rest. If all of them genuinely qualify,")
    print("that is a call for the user to make - ask, do not bypass with --no-verify.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
