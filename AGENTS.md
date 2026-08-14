# AGENTS.md

Universal instructions for AI coding agents working on this project.
Compatible with: Claude Code, Cursor, Cline, Aider, Continue, Windsurf, and any tool reading `AGENTS.md`.

This project follows **Agent-First (AF) methodology**. Full reference: `agent-first.md` in this folder.

---

## Agent entry points
ALWAYS start here when working on this project:
1. Read `documentation/project.yaml` to get the map of layers
2. Based on task, read relevant layer YAML (e.g. `documentation/backend_services.yaml`)
3. Use `code_path` + `entry` from manifest to jump directly to code
4. Do NOT grep the entire repo — use the manifest

## Task routing — choose workflow by task type

### Step 0 (all workflows) — does the task fit in one reviewable unit?

The binding question is not "how long will this take" but:

> **Can a reviewer, in a clean session with no implementation context, verify
> EVERY acceptance point of this task?**

If no → split before starting. A task too large to review never closes: the
Definition of Done never goes fully green and the review degrades into skimming.

Each part after splitting must have: one cognitively whole artifact; its own
acceptance criteria; an explicit **Out of scope** list; declared dependencies and
order; an independently mergeable end state. Name parts `N-a`, `N-b`, `N-c`.

Do NOT split when the parts would leave the repo in a broken intermediate state,
or when a part has no acceptance criteria of its own.

### New feature / new module → Full 9-step workflow
0. Size check — see Step 0 above; create the branch BEFORE the first commit
1. Orient — read project.yaml, find affected blocks
2. Read block context — output gotchas to user (mandatory)
3. ADR decision — apply 3-criteria rule
4. **4.0: context7 gate BEFORE the first edit or write.** Confirm against current
   docs every library API this task will touch, **including the test runner,
   assertion and mocking libraries**; training data is not an acceptable source;
   if an API cannot be confirmed, write nothing — confirm it or escalate.
   **4.1:** write tests for key scenarios per module, BEFORE implementation.
   The gate fires BEFORE the tests: a test file is code — it calls the runner's
   API, the assertion API, the mocking API, and the API of the module under test.
   Tests written from memory fail for the wrong reason and pin the implementation
   to an imagined API. "Write tests, then check docs" contradicts itself, because
   writing a test IS the first write.
5. Implement — code with sequential-thinking, KISS/DRY/SOLID/Feature-Based
6. Run tests — green → continue, red → fix
7. Update YAML — manifests of affected blocks
8. Self-Check — verify code against all cross-cutting rules (see checklist below)
9. Commit — pre-commit validates. Then review in a clean session before merge

### Self-Check checklist (step 8)
- [ ] context7: **verify step 4.0 happened BEFORE the first edit — tests included** — this box confirms the gate was passed, it does not replace it
- [ ] sequential-thinking: used for all non-trivial decisions during implementation?
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
Same as above. ADR likely "not needed", but tests are mandatory to prevent regression. Add gotcha if bug was non-obvious.

### Bug fix (trivial: typo, text, style) → Light workflow
1. Orient — read project.yaml, find affected block
2. Read block context — check gotchas
3. Fix
4. Commit

### Refactoring → Full 9-step workflow
Tests are critical — they prove behavior is preserved. YAML update mandatory since paths/structure change.

This routing applies to ALL tasks automatically, not only when user says "AF".

## When refactoring or adding features
1. Update corresponding YAML manifest if paths/summary/structure changed:
   - `code_path` / `entry` — if files moved
   - `summary` — if block purpose changed
   - `notes` — if key file added/removed
   - `api_calls` — if new endpoint
   - `depends_on` / `related_blocks` — if connections changed
2. Run `python documentation/validate.py` before committing
3. Pre-commit hook enforces reference integrity automatically

## Feature workflow (new features)
When implementing a new feature:

1. Read `documentation/project.yaml` → find affected blocks
2. Read affected blocks' YAML: summary, gotchas, notes, related_blocks
3. Decide if ADR is needed — apply 3-criteria rule:
   - Are there 2+ reasonable implementation paths?
   - Would someone in 6 months ask "why X not Y?"
   - Did deciding take >10 minutes on design?
   - All YES → create ADR BEFORE implementation, link via `adr: [N]` in block
   - Any NO → skip ADR, just implement
4. Implement the feature
5. Update YAML of affected blocks (fields listed above)
6. Add a gotcha if you stumbled on something non-obvious (budget: 1-2 per session)
7. Commit → pre-commit validates references

## ADR rules

- **ADR = Architecture Decision Record**, stored in `documentation/adr/NNN-kebab-title.md`
- **Create ADR BEFORE implementation**, never after — retrospective ADRs are forbidden
- **Format** (strict):
  ```markdown
  # ADR NNN: Short title
  Status: accepted
  Date: YYYY-MM-DD
  Affects: [block-name-1, block-name-2]

  ## Context
  What problem we're solving and why now.

  ## Decision
  What we decided and how it will be implemented.

  ## Consequences
  + Positive outcomes
  - Trade-offs and limitations
  ```
- **Two-way link**: block's `adr: [N]` + ADR's `Affects: [block-name]` — both required
- **Never modify existing ADRs** — if decision changes, create new ADR with `supersedes N`

## Gotchas (footguns) — self-maintaining documentation

When editing a block:
1. Read its `gotchas` and `notes` in YAML FIRST
2. **LIST all gotchas to the user** before starting implementation — never skip silently
3. If during work you discover a non-trivial detail future agents should know — ADD it to gotchas
4. Format: `"Don't X — reason Y"` (one short sentence)
5. **Budget: add at most 1-2 gotchas per session**. Don't spam the manifest.

Do NOT pre-fill gotchas from code analysis. Only add gotchas from real problems you encountered.

## Project-specific rules (Hard Rules)

Rules true only for this codebase — "never call X directly, it deadlocks", "every
schema change needs a migration in the same commit". These cause the outages, and
prose alone does not hold them.

**A rule is not finished until it has all four layers.** Give it a short stable id
(`H-1`, `V-1`) and use that id in every layer, so a failing hook and a checklist
line are visibly the same rule.

1. **Statement** — one line here: "Don't X — it causes Y"
2. **Executable check** — a grep or script that exits non-zero on violation
3. **Pre-commit hook** — the check wired in, scoped with `files:` to the paths it covers
4. **Review item** — the same check named in the clean-session review

**A red check that gates nothing is worse than no check** — it looks like coverage
while providing none.

Registry starts empty and is filled from this project's own incidents. Do NOT copy
rules from another project: they are domain-specific by construction, and a
checklist full of rules that do not apply trains the agent to skim the ones that do.

| id | rule | check |
|---|---|---|
| — | *(none yet)* | — |

## Closed investigations — do NOT re-open

Questions already settled, with the answer and the date. Without this an agent
re-investigates the same dead end every few months, at full cost each time.

Format: **`<topic>` — CLOSED `<date>`.** `<conclusion>` `<where the evidence lives>`

- *(none yet)*

## Cross-cutting quality rules (apply to ALL stages)

### 1. Always use context7 for documentation
Before reading, writing, or reviewing any code — check current documentation via context7.
Applies to: frameworks, libraries, standard library of the language, build tools, test tools, CLI tools.
**Never rely on training data.** API changes between versions, best practices evolve, deprecated patterns persist in training data.

### 2. Always use sequential-thinking for structured reasoning
Before and during implementation — use sequential-thinking for any non-trivial decision.
Applies to: ADR decisions, choosing implementation approach, evaluating trade-offs, debugging complex issues, refactoring strategy, mid-implementation design choices.
Structure: problem → options → trade-offs → decision. Never "shoot from the hip." If you hit a fork during coding — stop and think first.

### 3. Always apply KISS / DRY / SOLID when writing code
Apply during implementation, not as a separate review step:
- **KISS:** function > 40 lines → split; nesting > 3 levels → refactor
- **DRY:** grep project for similar logic before writing new code; 3 repetitions = abstraction threshold
- **SOLID:** single responsibility (S), extend don't modify (O), depend on abstractions (D)

### 4. Test-First at module level
- Write tests for key scenarios BEFORE implementation (per module, not per function)
- Always cover edge cases: null/empty inputs, network errors, invalid input, boundary values
- Implement → run tests → green = commit, red = fix
- Tests are the main safety net in agent-first — they verify behavior, YAML only verifies structure
- Register test commands in `project.yaml → tests`

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

## Git workflow

**One task = one branch.** Create it BEFORE the first commit; never work directly
on the default branch. Name it `<type>/<scope>-<slug>` mirroring the commit
convention: `feat/f11a-taxonomies`, `fix/reviews-depth-bug`, `docs/seo-plan`.

Branching costs nothing on a solo repo and keeps an escape hatch when a task turns
out wrong. It is independent of whether the project uses pull requests.

The merge model is per-project — check which one applies here:
- **Push to the default branch deploys** → branch, then merge locally. No
  `check-not-main` guard, no PR gate; they would break the deploy path.
- **PR-based** → branch, open a PR, merge only after green CI AND a clean-session
  review.

## Review is a gate, not a command

Nothing merges into the default branch until it has been reviewed in a clean
session with no implementation context. Self-review by the agent that wrote the
code is not a review — it is the same context grading its own work. Where CI is
absent or frozen, this is the ONLY gate. Exception: trivial changes (typo, copy,
styling) on the Light workflow.

## Agent autonomy rules

### Do without asking:
- Read code
- Run `scripts/validate.sh` or `python documentation/validate.py`
- Update YAML manifests after refactoring
- Create new ADRs when making architectural decisions
- Create a branch for the task

### Ask before:
- Deleting files
- Changing DB schema (migrations)
- Touching `.env` or config files
- Deploying to production
- Modifying existing ADRs (they are append-only)
- Merging without a clean-session review pass

### Never do:
- Commit directly to the default branch — always work in a task branch
- `git push --force`
- Commit secrets or `.env` files
- Modify ADRs retroactively (create new one with "supersedes N" instead)
- Skip pre-commit hooks (`--no-verify`) unless user explicitly allows

## Drift audit (periodic)

Every 2-4 weeks (or after major refactoring), user may run drift audit. When user asks to "provide drift audit" / "проведи дрейф-аудит":

1. For each block in each layer YAML:
   - Read `code_path` and list actual files
   - Verify `summary` still reflects purpose
   - Verify `notes` mentions current files, no dead references
   - Check for new important files missing from `notes`
2. Output a report in format:
   ```
   Block: <name>
     - [field]: [drift description] — [suggested fix]
   ```
3. DO NOT auto-edit YAML — wait for user approval per finding

## File layout reference

```
documentation/
├── project.yaml                    ← super-index, entry point for agents
├── <layer>.yaml                    ← blocks manifest per layer
├── validate.py                     ← integrity checker (incl. duplicate-key guard)
├── check-claude-md-sections.py     ← asserts AF sections survived edits
├── agent-first-guide.md            ← full methodology
└── adr/
    └── NNN-*.md                    ← append-only decision records

scripts/
└── validate.sh               ← unified validation command

.pre-commit-config.yaml       ← hook config
CLAUDE.md / AGENTS.md         ← agent instructions (this file)
```

## Quick reference: what to update when

| Code change | YAML field to update |
|---|---|
| Renamed/moved block file | `code_path`, `entry` |
| Block purpose changed | `summary` |
| Added/removed key file in block | `notes` |
| Added new API endpoint | `api_calls` |
| Made architectural decision | create ADR + add `adr: [N]` to block |
| Hit a footgun | add to `gotchas` (1-2 per session) |
| Changed inter-block dependency | `depends_on` / `related_blocks` |
| Created new code block | add new entry to layer YAML |

---

**Main principle:** Every token spent on "orientation" is a token not spent on the task.
YAML manifests provide cheap, accurate, machine-readable orientation.
