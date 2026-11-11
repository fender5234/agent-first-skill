# Upgrade Workflow

> Part of the `agent-first-setup` skill. Paths like `templates/…`, `guide.md`,
> `CHANGELOG.md` are relative to the skill root — the folder holding `SKILL.md`.


When user says "обнови проект под AF" / "upgrade AF" / similar — bring a project
that already has AF artifacts up to the methodology version this skill carries.

**Why this is a separate workflow and not setup.** The skill lives on the machine
(`~/.claude/skills/`); what setup put in the project — `documentation/validate.py`,
`scripts/validate.sh`, the CLAUDE.md sections — are COPIES that stopped tracking it
the moment they were written. They are forks, and a healthy project's fork is worth
MORE than the template: it has grown checks the template never had. Setup's rule
for a conflict is "overwrite". Here it is **merge**. Applying setup to a live
project behaves as a destructive operation, simply because nothing ever taught it
otherwise.

### The prime directive

> **Never overwrite a file the project has diverged on. Merge into it.**

Before writing to any file that already exists, diff it against the template. Every
difference is either (a) something this upgrade adds, or (b) something the project
added for itself. (b) is not noise to be cleaned up — it is the reason the project
works. Losing it is the worst outcome of this workflow, worse than the upgrade not
happening at all.

### Upgrade Steps

1. **Establish the delta.**
   - Read `documentation/project.yaml` → `meta.af_version`. **Absent means 1.0.0** —
     the field predates nothing else, so an old project simply lacks it.
   - Read `CHANGELOG.md` **in the skill root, next to `SKILL.md`**, in the skill's own directory. It
     ships with the skill precisely so an upgrade works on any machine without
     knowing where the source archive lives. Every entry newer than the project's
     version is in scope.
   - If the project's version equals the skill's — say so and stop. Do not
     "refresh" files that are already current.
   - **If no CHANGELOG is reachable, stop and say so.** Guessing the delta by
     diffing files is how project-specific checks get deleted as "drift".

2. **Ask the setup questions the project never answered.** Later versions add
   questions to Step 2 (`workflows/setup.md`) that did not exist when this project was set up. Ask them
   now, and treat the answers as binding for what gets generated. The
   deploy-model question is the dangerous one: generating a `check-not-main` guard
   into a project where a push to the default branch IS the deploy breaks the
   deploy path.

3. **Inventory what the project has, per file.** For each artifact the delta
   touches, record: does it exist, has it diverged from the template, and what is
   project-specific in it. Present this to the user before writing anything.

4. **Merge, file by file.**

   | Artifact | How |
   |---|---|
   | `documentation/validate.py` | Add new checks with the NEXT free number. Never renumber, never replace the file. A project check occupying number 7 stays at 7 |
   | `scripts/validate.sh` | Append new invocations. Existing lines are project gates — leave them |
   | `.pre-commit-config.yaml` | Add new hooks. Honour the deploy-model answer for conditional ones |
   | New standalone scripts | Copy as-is; nothing to conflict with |
   | `CLAUDE.md` / `AGENTS.md` | See step 5 — this is the one that needs care |
   | `documentation/project.yaml` | Set `meta.af_version` last, in step 7 |

5. **Repair CLAUDE.md, do not just append to it.** Setup appends sections that are
   missing and skips those whose heading already exists. That rule is wrong here:
   the common failure is a section that IS present but has lost content — a
   Self-Check checklist missing half its items still matches by heading, so setup
   would skip it and the gap would survive the upgrade.
   - Compare the project's version of each section against the template **item by
     item**, not by heading
   - Restore what is missing; keep every project-specific line
   - Where the project deliberately worded something differently, keep the
     project's wording and only add what is new
   - Watch for wording that was correct once and has since expired — a
     "tests are aspirational, no runner yet" caveat written before a test runner
     existed is now false and actively misleads

6. **Run both checks.** `python documentation/validate.py` and
   `python documentation/check-claude-md-sections.py` must both exit 0. A red
   sections check after an upgrade means step 5 was done by heading, not by item.

7. **Stamp the version.** Set `meta.af_version` in `documentation/project.yaml` to
   the skill's current version — last, only once 6 is green. A version stamp on a
   half-applied upgrade is worse than none: the next upgrade will skip the delta
   it claims to have applied.

8. **Report** — what was merged, what was skipped and why, what the user must
   decide. Name every project-specific thing you preserved, so the user can verify
   nothing was lost.

### Critical rules for upgrade

- **Merge, never overwrite** — see the prime directive
- **Absent `af_version` = 1.0.0**, not "unknown, re-run setup"
- **Do not renumber existing checks** — ids appear in commit messages, review
  checklists and CLAUDE.md prose; renumbering silently breaks all of them
- **Do not delete a project's checks as "drift"** — drift audit is a separate
  workflow with its own report-only rule, and it is not part of an upgrade
- **Stamp the version last**, after the gates are green
- **One project per session.** Two projects in one context is how a check from one
  ends up in the other

### Retrofitting `af_version` onto an older project

Projects set up before this field simply lack it. Do not treat that as corruption:
read it as 1.0.0, run the upgrade, and the stamp appears in step 7. There is no
separate migration for the field itself.
