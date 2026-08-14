#!/usr/bin/env python3
"""Asserts the AF sections actually landed in the project's agent instructions.

Why this exists: setup APPENDS sections to CLAUDE.md and then shows the user a
diff for approval. A long diff gets trimmed — by the user, or by the agent
summarising it — and the sections that get cut are invisible afterwards. Nothing
else notices: validate.py checks manifests, not instructions, and the project runs
fine for months with a workflow rule silently missing.

Observed failure this was written for: a project lost the Feature Review section,
both Test-First checklist items, and four of six Security checklist items during
setup. Discovered three months later, by hand.

Usage:
    python documentation/check-claude-md-sections.py            # checks CLAUDE.md
    python documentation/check-claude-md-sections.py AGENTS.md  # checks another file

Exit 0 when everything required is present, 1 otherwise. Safe in a pre-commit hook.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

# Headings the setup workflow is supposed to add. Each entry: (label, [aliases]).
# An alias matches case-insensitively as a substring of a heading line, so
# "## Agent entry points (Shipkit)" counts. Russian aliases are listed because
# project instructions are frequently not written in English — an English-only
# check reports a false miss on a section that is present under a translated name.
REQUIRED_SECTIONS = [
    ("Agent entry points", ["agent entry points", "точки входа"]),
    ("Task routing", ["task routing", "маршрутизация задач"]),
    ("Self-Check checklist", ["self-check"]),
    ("Feature review (clean session)", ["feature review", "ревью фичи", "проверь feature"]),
    ("Agent autonomy rules", ["agent autonomy", "автономи"]),
    ("Self-maintaining documentation", ["self-maintaining", "самодополн", "самоподдерж"]),
]

# Checklist lines that carry real weight and are the first thing dropped when a
# reviewer decides the diff is too long. Each entry: (label, [substrings]).
#
# Searched ONLY inside the Self-Check section, never the whole file. A project can
# discuss Test-First at length in its own prose while the checklist item itself is
# gone — a whole-file search calls that present, which is exactly the gap this
# script exists to catch.
REQUIRED_CHECKLIST_ITEMS = [
    ("context7 gate", ["context7"]),
    ("sequential-thinking", ["sequential-thinking"]),
    ("KISS", ["kiss"]),
    ("DRY", ["dry"]),
    ("SOLID", ["solid"]),
    ("Naming", ["naming", "именован"]),
    ("Test-First", ["test-first", "tests exist and pass", "тесты"]),
    ("Security — secrets", ["hardcoded secrets", "секрет"]),
    ("Security — injection", ["parameterized quer", "sql/nosql", "concatenat", "инъекц"]),
    ("Security — logs", ["sensitive data in logs", "no sensitive data", "в логах"]),
    ("Security — dependencies", ["known vulnerabilities", "npm audit", "pip-audit", "уязвим"]),
]


def heading_level(line: str) -> int:
    stripped = line.lstrip()
    return len(stripped) - len(stripped.lstrip("#"))


def extract_self_check(lines: list[str]) -> str | None:
    """Body of the Self-Check section: from its heading to the next heading of
    the same or higher level. Returns None when the section is absent."""
    start = None
    level = 0
    for i, line in enumerate(lines):
        if line.lstrip().startswith("#") and "self-check" in line.lower():
            start = i + 1
            level = heading_level(line)
            break
    if start is None:
        return None

    for j in range(start, len(lines)):
        line = lines[j]
        if line.lstrip().startswith("#") and heading_level(line) <= level:
            return "\n".join(lines[start:j])
    return "\n".join(lines[start:])


def check(target: Path) -> int:
    if not target.exists():
        print(f"ERROR: {target} not found")
        return 1

    text = target.read_text(encoding="utf-8")
    lines = text.splitlines()
    headings = [ln.strip().lower() for ln in lines if ln.lstrip().startswith("#")]

    missing_sections = [
        label for label, aliases in REQUIRED_SECTIONS
        if not any(a in h for h in headings for a in aliases)
    ]

    self_check = extract_self_check(lines)
    if self_check is None:
        # The section itself is already reported missing above; listing every item
        # inside it as separately missing would bury that one real finding.
        missing_items = []
    else:
        scope = self_check.lower()
        missing_items = [
            label for label, needles in REQUIRED_CHECKLIST_ITEMS
            if not any(n in scope for n in needles)
        ]

    if not missing_sections and not missing_items:
        print(f"OK: {target.name} has all required AF sections and checklist items")
        return 0

    print(f"MISSING in {target.name}:")
    for s in missing_sections:
        print(f"  - section: ## {s}")
    for i in missing_items:
        print(f"  - checklist item: {i}")
    print()
    print("Source of truth: the skill's templates/claude-md-sections.md.")
    print("If a section is deliberately absent, delete it from REQUIRED_* above")
    print("and write down why — an unexplained exclusion reads as an oversight.")
    return 1


if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "CLAUDE.md"
    sys.exit(check(ROOT / name))
