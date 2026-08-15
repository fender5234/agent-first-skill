#!/usr/bin/env python3
"""Refuses `git commit` while HEAD is on the default branch.

One task = one branch. The rule was prose in CLAUDE.md and prose lost: across ten
commits of real work, every rule with a machine check held and every rule with only
a statement was broken. This is the check for that one.

**It does not interfere with deploy-on-push**, which is how shipkit ships. The
obvious guess — "a branch guard blocks the deploy" — is wrong, mechanically:

  * it is a pre-commit hook, so it never runs on `git push`;
  * with branch -> `merge --ff-only` -> push, no commit is ever created on main,
    so it does not fire once;
  * merges invoke `pre-merge-commit`, which pre-commit does not install by default.

Detached HEAD is allowed on purpose: that is what a rebase or a `git bisect` looks
like, and failing there would break operations that are not "committing to main".

Usage:
    python scripts/check-not-main.py           # guards against "main"
    python scripts/check-not-main.py master    # guards against another branch name

Exit 0 when on a task branch, 1 when on the default branch.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DEFAULT_BRANCH = "main"


def current_branch() -> str:
    r = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return r.stdout.strip()


def main(argv: list[str]) -> int:
    protected = argv[0] if argv else DEFAULT_BRANCH
    branch = current_branch()

    if branch != protected:
        return 0

    print(f"Refusing to commit directly to '{protected}'.")
    print()
    print("One task = one branch, created BEFORE the first commit. Name it")
    print("<type>/<scope>-<slug>, mirroring the commit convention:")
    print("  feat/f11a-taxonomies, fix/reviews-depth-bug, docs/seo-plan")
    print()
    print("Move this work onto a branch without losing it:")
    print(f"  git checkout -b <type>/<scope>-<slug>")
    print()
    print(f"Then commit there, merge back with --ff-only, and push. On shipkit a")
    print(f"push to '{protected}' deploys, so the branch is the only step between a")
    print("half-finished change and production.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
