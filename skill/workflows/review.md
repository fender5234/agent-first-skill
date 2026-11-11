# Feature Review Workflow

> Part of the `agent-first-setup` skill. Paths like `templates/…`, `guide.md`,
> `CHANGELOG.md` are relative to the skill root — the folder holding `SKILL.md`.


When user says "Проверь Feature N по AF" / "Review Feature N" / "Проверь выполненную задачу" — run independent review in a **clean session** (no implementation context).

The purpose: a fresh agent reviews code written by another agent (or the same agent in a previous session). Like a code review by someone who didn't write the code.

**This is a gate, not an optional command.** No task merges into the default branch
until it has passed a review in a clean session. Where a project has CI, this runs
alongside it; where CI is absent or frozen, it is the ONLY gate — say so explicitly
in the project's CLAUDE.md so nobody treats it as advisory. The one exception is
trivial changes (typo, copy, styling) routed to the Light workflow.

### Recommended development cycle

```
Session 1:  "Выполни Feature N по AF workflow"    → implementation (9-step)
Session 2:  "Проверь Feature N по AF"              → independent review
            → all PASS → push → next feature
```

Each feature = new session. Each review = new session. Clean context every time.

### Review Steps

1. **Read plan** — find Feature N acceptance criteria (full list of checkboxes).

   **When there is no acceptance list, do not invent one.** A review run on a
   trivial change — a moved button, a copy tweak — has nothing formal to check
   against, and manufacturing criteria after the fact produces a review that passes
   by construction. Say plainly that there is no acceptance list, then review what
   is actually reviewable: the diff touches only what it should, the gates are
   green, project-specific rules hold, anything visual is marked MANUAL. A short
   honest report beats a long fabricated one.

   Where criteria DO exist, also check they were not edited to match the result —
   see step 7.
2. **Read manifests** — `documentation/project.yaml` → relevant layer YAML → gotchas and notes of affected blocks
3. **Read project-specific plans** — if project has implementation plans (e.g. `db-creation-plan.md`), read relevant sections
4. **Check each acceptance point:**
   - File/code exists and matches description
   - Tests exist and pass
   - `[manual]` items — mark as "requires manual verification"
5. **Run automated checks:**
   - Lint, typecheck, tests, build (project-specific commands from `project.yaml → tests`)
   - `python documentation/validate.py`
   - **Everything needed is committed — check this even though the gates are green.**
     The reviewer works in a clean *session*, not a clean *checkout*: same working
     tree, same installed dependencies, same local env. A file created and never
     `git add`ed builds fine here and is simply absent from a fresh clone. No gate
     above sees it, because every one of them reads the working tree.

     Minimum: `git status --porcelain` is empty, and
     `git ls-files --others --exclude-standard` lists nothing the build imports.
     For a large change, do it properly — build from a throwaway `git worktree` of
     the branch, which is a real clean checkout without waiting on CI.

     This matters most where a push to the default branch deploys: there is no
     intermediate step between a forgotten `git add` and production.
   - **Migration integrity (if the project uses DB migrations):** green tests/build do NOT prove the migrations are complete. Test suites that use schema `push`/`sync` (auto-create columns from code, bypassing the migration files) mask incomplete migration SQL — and a snapshot-vs-code drift check passes when the migration's *snapshot* is complete even though its hand-written `up()` SQL is not. So a migration can be green on every gate yet break a freshly-migrated DB (missing column/table/index at runtime). Verify separately: apply migrations from scratch to a throwaway DB (migrations-only, NOT push), diff the resulting schema against the code-derived schema, and smoke-test the app's main entrypoint (e.g. admin/home) against that DB. Prefer a repo script for this; if none exists, flag it as a gap. Highest risk on type-changing or hand-written migrations.
6. **Verify cross-cutting rules** (`rules/quality.md`, grep-based):
   - Security: no hardcoded secrets, no SQL concatenation
   - Naming: consistent with project patterns
   - Architecture: feature-based structure respected
   - Project-specific rules (from CLAUDE.md)

7. **Audit the claims the author made about their own work.** This is the reviewer's
   highest-value pass, because it is the only defect class no gate catches: lint,
   tests, build and validate.py all stay green while a comment, a gotcha or an ADR
   says something untrue about the code beside it.

   For every claim that something is *covered / protected / prevented / guaranteed*
   by a test — find the test and read what it actually asserts. A test written as a
   tripwire but never wired to fail documents the hazard rather than guarding it.
   Where the claim is load-bearing, break the thing it protects and confirm the
   suite goes red.

   Observed once, in a real session: three places — a source comment, a manifest
   gotcha and an ADR's Consequences — stated that the composition order of two
   functions was protected by a test. Reordering the calls left all four gates
   green and reintroduced the bug on nine indexed pages.

   Also check: does a rule the workflow required actually have an artifact? "wrote
   tests first" with the tests committed after the implementation, "used
   sequential-thinking" with no named forks.

8. **Verify the process rules that have no machine gate.** Branch used, gotcha
   budget respected, no existing ADR's decision rewritten. Two of these now have
   pre-commit hooks; name in the report which held by hook and which by inspection.
9. **Output report:** table of acceptance points with statuses (PASS / FAIL / MANUAL)
10. **Verdict:**
    - All PASS → "Feature N ready for push/merge"
    - Any FAIL → list specific problems with file paths and line numbers

### Fix policy

By default — **report only**, no fixes.
If user asks to fix found problems ("исправь", "почини", "fix"):
- **Minor** (lint errors, missing test, typo) — fix in current session
- **Major** (architecture, module redesign) — warn user and suggest new session
- When fixing: apply ALL cross-cutting rules (context7, sequential-thinking, KISS/DRY/SOLID)
- After fixes: re-run steps 5-6 to verify

### Output format

```
📋 AF Feature Review: Feature N

Acceptance:
  ✅ PASS  — acceptance point 1 (file: src/...)
  ✅ PASS  — acceptance point 2 (test: tests/...)
  ❌ FAIL  — acceptance point 3: [description of problem]
  👁 MANUAL — acceptance point 4 (requires visual check)

Automated checks:
  ✅ lint: 0 errors
  ✅ typecheck: 0 errors
  ✅ tests: 15 passed, 0 failed
  ✅ build: success
  ✅ validate.py: OK

Cross-cutting rules:
  ✅ Security: no issues found
  ✅ Naming: consistent
  ❌ Architecture: [specific violation]

Verdict: N PASS, M FAIL, K MANUAL
[Ready for push / Needs fixes — see FAIL items above]
```

### Critical rules for review

- **DO NOT auto-fix** without user's explicit request
- **Check EVERY acceptance point** — don't skip or summarize
- **Be specific in FAIL descriptions** — file path, line number, what's wrong, what's expected
- **Cross-cutting rules apply to the reviewer too** — use context7 to verify API usage is current, use sequential-thinking if unsure about a finding
