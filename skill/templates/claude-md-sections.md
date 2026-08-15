# Sections to add to CLAUDE.md

Copy these sections into the project's CLAUDE.md file.

---

## Agent entry points
ALWAYS start here when working on this project:
1. Read `documentation/project.yaml` to get the map
2. Based on task, read relevant layer YAML (e.g. `documentation/frontend.yaml`)
3. Use `code_path` + `entry` from manifest to jump directly to code
4. Do NOT grep the entire repo — use the manifest

## Task routing — choose workflow by task type

Before starting any task, classify it and follow the appropriate workflow:

### Step 0 (all workflows) — does the task fit in one reviewable unit?

The binding question is not "how long will this take" but:

> **Can a reviewer agent, in a clean session with no implementation context,
> verify EVERY acceptance point of this task?**

If no → split before starting. A task too large to review never closes: the
Definition of Done never goes fully green and the review degrades into skimming.

Each part after splitting must have: one cognitively whole artifact; its own
acceptance criteria; an explicit **Out of scope** list; declared dependencies and
order; and an independently mergeable end state. Name parts `N-a`, `N-b`, `N-c`
and keep the umbrella name in forward references.

Do NOT split when the parts would leave the repo in a broken intermediate state,
or when a part has no acceptance criteria of its own.

### New feature / new module → Full 9-step workflow
0. Size check — see Step 0 above; branch before the first commit
1. Orient — read project.yaml, find affected blocks
2. Read block context — output gotchas to user (mandatory)
3. ADR decision — apply 3-criteria rule
4. **4.0: context7 gate BEFORE the first Edit/Write** — confirm against current docs
   every library API this task touches, **including the test runner, assertion and
   mocking libraries**; training data is not a source; API unconfirmed → write
   nothing. **4.1:** tests for key scenarios per module, BEFORE implementation.
   The gate fires BEFORE the tests — a test file is code, and writing one IS the
   first Write. Tests written from memory fail for the wrong reason and pin the
   implementation to an imagined API
5. Implement — code with sequential-thinking, KISS/DRY/SOLID/Feature-Based
6. Run tests — green → continue, red → fix
7. Update YAML — manifests of affected blocks
8. Self-Check — verify code against all cross-cutting rules (see checklist below)
9. Commit — pre-commit validates. Then review in a clean session before merge

### Self-Check checklist (step 8)
- [ ] context7: **verify step 4.0 happened BEFORE the first Edit/Write — tests included** — this box confirms the gate was passed, it does not replace it. Ticking it afterwards, having written the code from memory, is the failure this wording exists to prevent
- [ ] sequential-thinking: **name the forks it was used on.** Reasoning done silently is unverifiable, which is the whole point of the rule. "Used it" with nothing to point at means it was not used
- [ ] **Claims about your own work are verified, not intended.** For every statement that something is covered, protected, prevented or guaranteed by a test — did you watch that test go red with the protection removed? A test written as a tripwire that never fired is documentation of the hazard, not a guard against it. Unverified claims of this kind are the one defect class no machine gate catches
- [ ] KISS: no functions > 40 lines, no nesting > 3 levels?
- [ ] DRY: grepped project for similar logic, no unnecessary duplication?
- [ ] SOLID: each new module/class has single responsibility?
- [ ] Feature-Based: new code inside features/[name]/, not in root or wrong folder?
- [ ] Feature-Based: no direct imports from another feature's internals (only via index.ts)?
- [ ] Feature-Based: nothing added to shared/ that's used by only 1 feature?
- [ ] Naming: new names follow existing project patterns (grepped before naming)?
- [ ] Naming: one domain = one root word, no synonyms mixing?
- [ ] Naming: no generic names (utils.ts, helpers.ts) without domain prefix?
- [ ] Security: no hardcoded secrets (API keys, passwords, tokens) in code?
- [ ] Security: no SQL/NoSQL string concatenation — use parameterized queries?
- [ ] Security: user input validated/sanitized before use?
- [ ] Security: no sensitive data in logs or error messages?
- [ ] Security: no CORS wildcard (*) in production config?
- [ ] Security: new dependencies checked for known vulnerabilities?
- [ ] Test-First: tests exist and pass for new/changed modules?
- [ ] Test-First: edge cases covered (null, empty, errors, invalid input, boundaries)?
If any check fails — fix before committing.

### Bug fix (logic/behavior) → Full 9-step workflow
Same as above. ADR will likely be "not needed" (step 3), but tests are mandatory — to prevent the bug from returning. Add gotcha describing the bug if non-obvious.

### Bug fix (trivial: typo, text, style) → Light workflow
1. Orient — read project.yaml, find affected block
2. Read block context — check gotchas
3. Fix
4. Commit — pre-commit validates

No tests, no ADR, no YAML update needed for trivial fixes.

### Refactoring → Full 9-step workflow
Tests are critical — they prove behavior is preserved. YAML update is mandatory since paths/structure likely change.

### Feature review (separate clean session) → command: "Проверь Feature N по AF"

**This is a gate, not an optional command.** Nothing merges into the default branch
until it has passed a review in a clean session. Where CI exists this runs alongside
it; where CI is absent or frozen, it is the ONLY gate — say so here explicitly so
nobody reads it as advisory. Exception: trivial changes routed to the Light workflow.

Run in a **new session** (without implementation context) for independent verification.
The reviewer agent MUST:
1. Read project plan → Feature N acceptance (full list of points)
2. Read `documentation/project.yaml` → relevant layer YAML → gotchas and notes
3. For EACH acceptance point verify: code exists, tests exist and pass, `[manual]` items noted
4. Run: lint, typecheck, tests, build (commands from `project.yaml → tests`)
5. Run: `python documentation/validate.py`
6. Verify cross-cutting rules via grep (security, naming, architecture)
7. Output report: table of acceptance points with PASS / FAIL / MANUAL
8. Verdict: all PASS → "ready for push/merge", any FAIL → list problems with file paths

By default — **report only**, no fixes.
If user asks to fix ("исправь", "fix"):
- Minor (lint, missing test, typo) — fix in current session
- Major (architecture, redesign) — warn and suggest new session
- When fixing: apply ALL cross-cutting rules (context7, sequential-thinking, KISS/DRY/SOLID)
- After fixes: re-run automated checks

Recommended development cycle:
```
Session 1:  "Выполни Feature N по AF workflow"    → implementation
Session 2:  "Проверь Feature N по AF"              → independent review
            → all PASS → push → next feature
```

This routing applies to ALL tasks automatically, not only when user says "AF".

## Git workflow

**One task = one branch.** Create it BEFORE the first commit; never work directly
on the default branch. Name it `<type>/<scope>-<slug>` mirroring the commit
convention: `feat/f11a-taxonomies`, `fix/reviews-depth-bug`, `docs/seo-plan`.

Branching costs nothing on a solo repo and keeps an escape hatch when a task turns
out wrong. It is independent of whether the project uses pull requests.

The `check-not-main` pre-commit guard enforces this. **It is compatible with a
deploy-on-push setup** — the obvious guess is wrong. It is a pre-commit hook: it
refuses `git commit` while HEAD is on the default branch. It never runs on
`git push`, so it cannot block a deploy; with `branch → merge --ff-only → push` no
commit is created on the default branch, so it does not fire at all; and merges
invoke `pre-merge-commit`, not `pre-commit`.

> **Fill in during setup — how does this project merge?**
>
> - **Push to the default branch deploys** → branch, merge locally, push. No PR gate.
> - **PR-based** → branch, open a PR, merge only after a green CI run AND a
>   clean-session review.
>
> Both models get the `check-not-main` guard. Delete the line that does not apply
> and state which model this project uses.

## Agent autonomy rules

### Do without asking:
- Read code
- Run `scripts/validate.sh`
- Update YAML manifests after refactoring
- Create new ADRs when making decisions
- Create a branch for the task

### Ask before:
- Deleting files
- Changing DB schema (migrations)
- Touching .env or config
- Deploying to production
- Modifying an existing ADR's Context / Decision / Consequences (append-only)
- Merging without a clean-session review pass

### Never do:
- Commit directly to the default branch — always work in a task branch
- push --force
- Commit secrets / .env
- Rewrite an ADR's Context / Decision / Consequences retroactively — supersede with a new ADR instead. **`Affects:` is exempt**: it is a cross-reference index, not the decision, and `validate.py` check 4 requires it to name every block that declares `adr: [N]`. Adding a consumer to it needs no permission
- Skip pre-commit hooks (`--no-verify`)

## Cross-cutting quality rules

### 1. Always use context7 for documentation
Before reading, writing, or reviewing any code — check current documentation via context7.
Applies to: frameworks, libraries, standard library, build/test tools.
Never rely on training data — API and best practices change between versions.

### 2. Always use sequential-thinking for decisions
Before and during implementation — use sequential-thinking for any non-trivial decision.
Applies to: ADR decisions, implementation approach, trade-offs, debugging, refactoring, mid-implementation design choices.
Structure: problem → options → trade-offs → decision. If you hit a fork during coding — stop and think first.

### 3. Always apply KISS / DRY / SOLID when writing code
- KISS: function > 40 lines → split; nesting > 3 levels → refactor
- DRY: grep project for similar logic before writing new code; 3 repetitions = abstraction threshold
- SOLID: single responsibility (S), extend don't modify (O), depend on abstractions (D)

### 4. Test-First at module level
- Write tests for key scenarios BEFORE implementation (per module, not per function)
- Always cover edge cases: null/empty inputs, network errors, invalid input, boundary values
- Implement → run tests → green = commit, red = fix
- Tests are the main safety net — they verify behavior, YAML only verifies structure

### 5. Always use Feature-Based Architecture
- Structure: features/ (one folder per business capability) + shared/ (only code used by 2+ features)
- Colocation: components, hooks/services, types, tests — all inside the feature folder
- Features import each other only through index.ts (public API)
- Move to shared/ only when actually used in 2+ features, not preemptively
- Anti-pattern: layer-based grouping (controllers/, services/, models/)

### 6. Follow consistent Naming Conventions
- Before naming anything — grep project for existing patterns and follow them exactly
- One domain = one root word everywhere (order, not purchase/item/product interchangeably)
- No generic names (utils.ts, helpers.ts) — always prefix with domain (orderUtils.ts)
- No abbreviations in file names (usr → user; auth is ok — it's a domain term)
- New feature naming must match the pattern of existing features

### 7. Apply Security basics during implementation
- Use parameterized queries — never concatenate user input into SQL/NoSQL
- Validate/sanitize all user input at entry points; always validate server-side
- Secrets in env vars or secret managers — never hardcode in source
- Never log sensitive data (passwords, tokens, PII)
- No CORS wildcard (*) in production; no secrets in version control
- Check new dependencies for known vulnerabilities before adding

## Project-specific rules (Hard Rules)

Rules true only for this codebase — "never call X directly, it deadlocks", "every
schema change needs a migration in the same commit". These cause the outages, and
prose alone does not hold them.

**A rule is not finished until it has all four layers.** Give it a short stable id
and use that id in every layer, so a failing hook and a checklist line are visibly
the same rule.

| Layer | What |
|---|---|
| 1. Statement | one line here: "Don't X — it causes Y" |
| 2. Executable check | a grep or script that exits non-zero on violation |
| 3. Pre-commit hook | the check wired into `.pre-commit-config.yaml`, scoped with `files:` |
| 4. Review item | the same check named in the clean-session review |

**A red check that gates nothing is worse than no check** — it looks like coverage
while providing none. If one cannot be wired up yet, record that here with the reason.

### Registry

Start empty; fill from this project's own incidents. Do NOT copy rules from another
project — they are domain-specific by construction, and a checklist full of rules
that do not apply trains the agent to skim the ones that do.

| id | rule | check |
|---|---|---|
| — | *(none yet)* | — |

## Closed investigations — do NOT re-open

Questions already settled, with the answer and the date. Without this an agent
re-investigates the same dead end every few months, at full cost each time.

Format: **`<topic>` — CLOSED `<date>`.** `<conclusion>` `<where the evidence lives>`

- *(none yet)*

## Self-maintaining documentation rules

### When editing a block:
1. Before changes: read its gotchas and notes in the YAML manifest
2. **LIST all gotchas to the user** before starting implementation — never skip silently
3. If you discover a non-trivial detail during work that future agent
   should know — ADD IT to gotchas
4. If you make architectural decision — create ADR and link in adr: []

### When reading code reveals a "footgun":
- Add a short gotcha to the block in YAML
- Format: "Don't X — reason Y" (one sentence)

### Budget: add at most 1-2 gotchas per session
Don't spam the manifest — only genuinely important things.
