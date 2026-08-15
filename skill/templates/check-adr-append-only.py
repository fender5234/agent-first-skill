#!/usr/bin/env python3
"""Rejects edits to an existing ADR's decision. Allows the `Affects:` index.

Why this exists. Two rules in this methodology looked like a contradiction:

  * CLAUDE.md — ADRs are append-only; ask before modifying one
  * validate.py check 4 — an ADR's `Affects:` must name every block that
    declares `adr: [N]`

So adding a new block that depends on an existing decision FORCES an edit to that
ADR. Observed once in a real session: validate.py blocked the commit, the agent
found a precedent for the same edit in the ADR history, and unblocked itself
instead of asking. A rule that cannot be obeyed teaches that rules are negotiable.

The resolution is a distinction, not an exception: `Affects:` is a cross-reference
index maintained by the validator, not part of the decision. Context, Decision,
Consequences and the alternatives are the decision — those stay append-only, and
are superseded by a NEW ADR rather than rewritten.

This script enforces exactly that line.

Usage (pre-commit passes the staged files, or run it bare to check them yourself):
    python documentation/check-adr-append-only.py [file ...]

Exit 0 when clean, 1 when a decision was edited.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
ADR_DIR = "documentation/adr"

# A changed line is tolerated when it is the Affects index. Matches the plain
# form and the markdown bullet/bold form both conventions produce.
AFFECTS_RE = re.compile(r"^[-*\s]*\**\s*affects\s*:?\s*\**", re.IGNORECASE)


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True
    ).stdout


def staged_adr_files() -> list[str]:
    """Staged files under the ADR dir, excluding newly added ones.

    A new ADR is not an edit — it is the intended way to record a decision, and
    superseding works by adding one. Only 'M' matters here.
    """
    out = git("diff", "--cached", "--name-status", "--diff-filter=M")
    files = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2 and parts[1].startswith(ADR_DIR) and parts[1].endswith(".md"):
            files.append(parts[1])
    return files


def offending_lines(path: str) -> list[str]:
    """Changed lines in the staged diff that are not the Affects index."""
    diff = git("diff", "--cached", "-U0", "--", path)
    bad = []
    for line in diff.splitlines():
        if line.startswith(("+++", "---", "@@", "diff ", "index ")):
            continue
        if not line.startswith(("+", "-")):
            continue
        body = line[1:]
        if not body.strip():
            continue  # blank-line churn is not a decision change
        if AFFECTS_RE.match(body):
            continue
        bad.append(line)
    return bad


def main(argv: list[str]) -> int:
    targets = [a for a in argv if a.startswith(ADR_DIR)] or staged_adr_files()
    if not targets:
        return 0

    failures = {}
    for path in targets:
        bad = offending_lines(path)
        if bad:
            failures[path] = bad

    if not failures:
        return 0

    print("ADRs are append-only - the decision was edited, not just the index:")
    for path, lines in failures.items():
        print(f"\n  {path}")
        for line in lines[:8]:
            print(f"    {line}")
        if len(lines) > 8:
            print(f"    ... and {len(lines) - 8} more changed lines")
    print()
    print("Allowed without asking: the `Affects:` line - it is a cross-reference")
    print("index, and validate.py check 4 requires it to name every block that")
    print("declares adr: [N].")
    print()
    print("To change a decision: write a NEW ADR that says 'supersedes NNN'.")
    print("If this edit is genuinely right anyway, that is a call for the user to")
    print("make - ask, do not bypass with --no-verify.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
