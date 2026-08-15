---
name: agent-first-setup
description: Set up or migrate a project to agent-first architecture with YAML manifests, ADRs, validation, and pre-commit hooks. Also runs drift-audit to verify YAML manifests match reality, upgrades a project already on AF to a newer methodology version (merging, never overwriting its own checks), guides feature-implementation workflow (when to create ADRs, which YAML fields to update), and provides independent feature review in clean sessions. Use when user mentions "AF" (shorthand for agent-first), or asks to "setup agent-first", "make project agent-friendly", "add YAML manifests", "organize project for AI agents", "внедри agent-first", "настрой проект под агентов", "agent-first подход", "используй AF", "примени AF", "настрой AF", "проведи дрейф-аудит", "drift audit", "дрейф аудит", "проверь соответствие yaml коду", "сверь манифесты с кодом", "обнови проект под AF", "обнови проект под новый скилл", "апгрейд AF", "upgrade AF", "обнови AF до текущей версии", "перенеси изменения скилла в проект", "добавь фичу по AF", "новая фича AF", "implement feature AF", "AF workflow", "нужен ли ADR", "do I need ADR", "проверь Feature", "проверь фичу", "review Feature", "проверь выполненную задачу"
---

# Agent-First Project Setup

Methodology for organizing projects for AI-agent-driven development and maintenance.

## Full reference
Read `guide.md` for complete methodology, principles, and rationale.
Read `CHANGELOG.md` for what changed between methodology versions — the Upgrade
Workflow diffs a project's `meta.af_version` against it.

## Templates (ready to copy)
- `templates/project.yaml` — super-index for the project
- `templates/layer.yaml` — blocks manifest template
- `templates/validate.py` — integrity checker (paths, ADR cross-refs, orphan detection, duplicate keys)
- `templates/check-claude-md-sections.py` — asserts the AF sections survived setup
- `templates/check-adr-append-only.py` — an ADR's decision is immutable, its `Affects:` index is not
- `templates/check-gotcha-budget.py` — caps gotchas added to pre-existing blocks
- `templates/check-not-main.py` — refuses `git commit` on the default branch
- `templates/pre-commit-config.yaml` — pre-commit hook config
- `templates/validate.sh` — unified validation script
- `templates/adr-template.md` — ADR skeleton
- `templates/claude-md-sections.md` — sections to add to CLAUDE.md
- `templates/ci-validate.yml` — GitHub Actions workflow for PR validation
- `templates/generate-manifest.py` — auto-generate skeleton layer.yaml from directory
- `templates/yaml-to-mermaid.py` — generate Mermaid dependency graph from manifests

## Operator guide
Read `operator-guide.md` for how the operator (human) should interact with the agent during AF workflows.

## Cross-cutting rules (apply to ALL workflows)

These rules are mandatory at every stage — orientation, ADR decisions, implementation, drift audit, review.

### 1. Always use context7 for documentation
Before reading, writing, or reviewing any code — check current documentation via context7.
This applies to: frameworks, libraries, standard library of the language, build tools, test tools, CLI tools.
**Never rely on training data.** API changes between versions, best practices evolve, deprecated patterns persist in training data.

### 2. Always use sequential-thinking for structured reasoning
Before and during implementation — use sequential-thinking MCP server for any non-trivial decision.
This applies to: ADR decisions, choosing implementation approach, evaluating trade-offs, debugging complex issues, refactoring strategy, and mid-implementation design choices.
**Never "shoot from the hip."** Structure your reasoning: problem → options → trade-offs → decision.
If during coding you hit a fork ("should I do X or Y?") — stop and use sequential-thinking before proceeding.

### 3. Always apply KISS / DRY / SOLID when writing code
Apply these principles during implementation, not as a separate review step:

**KISS:**
- Function > 40 lines → split
- Nesting > 3 levels → refactor
- If code needs a "why" comment — consider if the solution is too complex

**DRY:**
- Before writing new code — grep the project for similar logic
- If 70%+ overlap found — reuse, don't duplicate
- 3 repetitions = threshold for abstraction (not before)
- **UI widgets specifically:** before building a repeatable widget (rating stars, chip, badge, uploader, etc.) grep NOT ONLY the shared-component registry/manifest, but also `features/**` + the shared-UI dir for the visual pattern (icon name / signature class). The registry catches only what's *already* extracted; inline duplication living inside feature components is caught ONLY by grepping code. Copying the nearest open reference file is the failure mode — search first, then on the 2nd–3rd copy extract to shared.

**SOLID (adapted):**
- S — one module/class = one responsibility
- O — new functionality via extension, not modification of existing code
- D — depend on abstractions, not concrete implementations

### 4. Test-First at module level
Write tests BEFORE implementation for each module/feature:

1. Write tests for key scenarios of the module (not per function — per module)
2. Write implementation
3. Run tests — green → commit, red → fix → rerun
4. Register test commands in `project.yaml → tests` so agents know what to run

**Always cover edge cases explicitly:**
- Null / undefined / empty inputs
- Empty arrays and collections
- Network errors, timeouts, API returning 4xx/5xx
- Invalid or malformed user input
- Concurrent requests / race conditions (if applicable)
- Boundary values (0, negative, max int, empty string)

**Not classic TDD** (red-green-refactor per function — too expensive in tokens).
Test-First per module: one cycle of tests → implementation → verification.
Tests are the main safety net in agent-first — they verify behavior, YAML manifests only verify structure.

### 5. Always use Feature-Based Architecture for code organization
Organize code by business feature, not by technical layer:

**Structure:**
- `features/` (or `modules/`) — one folder per business capability
- `shared/` — only code used by 2+ features
- Each feature folder contains its own components, hooks/services, types, tests

**Rules:**
- Everything related to a feature lives in its folder (colocation principle)
- Features import each other only through index.ts (public API)
- Move to shared/ only when actually used in 2+ features, not preemptively
- 1 feature = 1 user-facing capability, describable in one sentence

**Anti-patterns:**
- Layer-based grouping (controllers/, services/, models/) — splits features across folders
- Premature shared/ — extracting "just in case" before 2+ usages exist
- Deep cross-feature imports bypassing index.ts

### 6. Follow consistent Naming Conventions for agent-friendliness
Before creating any file, variable, or function — grep the project for existing naming patterns and follow them exactly.

**Files:**
- Feature folder: plural noun (orders/, users/, payments/)
- Components: PascalCase matching feature (OrderList.tsx, OrderCard.tsx)
- Hooks: use + feature name (useOrders.ts, useCart.ts)
- API: feature + Api (orderApi.ts, userApi.ts)
- Types: feature + Types (orderTypes.ts, userTypes.ts)
- Tests: same name + .test (OrderList.test.tsx)

**Greppability:**
- One domain = one root word everywhere (order, not purchase/item/product interchangeably)
- No abbreviations in file names (usr → user; auth is ok — it's a domain term)
- No generic names (utils.ts, helpers.ts, misc.ts) — always prefix with domain (orderUtils.ts)

**Predictability:**
- If pattern exists — follow it exactly, don't invent synonyms
- Before naming anything — grep project for existing conventions
- New feature naming must match the pattern of existing features

### 7. Apply Security basics during implementation
Write secure code from the start, not as an afterthought:

**Always:**
- Use parameterized queries for SQL/NoSQL — never concatenate user input into queries
- Validate and sanitize all user input at entry points
- Store secrets in environment variables or secret managers — never hardcode in source
- Use HTTPS for all external communications

**Never:**
- Log sensitive data (passwords, tokens, PII, full credit card numbers)
- Use CORS wildcard (*) in production
- Commit secrets, .env files, or credentials to version control
- Trust client-side validation alone — always validate server-side too

**On adding dependencies:**
- Check for known vulnerabilities before adding (npm audit, pip-audit, etc.)
- Prefer well-maintained packages with recent updates

## Project-specific rules — the Hard Rules pattern

The seven rules above are universal. Every real project also accumulates rules that
are true only for it: "in this codebase, never call X directly — it deadlocks",
"every schema change needs a migration file in the same commit". These are the ones
that actually cause outages, and prose in CLAUDE.md does not hold them.

**A project rule is not finished until it has all four of these:**

| Layer | What it is | Why it alone is not enough |
|---|---|---|
| 1. **Statement** | one line in CLAUDE.md: "Don't X — it causes Y" | Prose is skippable. Agents read past it under load |
| 2. **Executable check** | a grep or a script that exits non-zero on violation | Without a machine check, compliance is self-reported |
| 3. **Pre-commit hook** | the check wired into `.pre-commit-config.yaml`, scoped by `files:` to the paths it applies to | An unwired script rots. It goes red and nobody notices |
| 4. **Review checklist item** | the same check named in the Feature Review Workflow | Pre-commit can be bypassed with `--no-verify`; the clean-session review cannot |

Give each rule a short stable id (`H-1`, `V-1`, `E-1`) and use that id in all four
places, so a failing hook, a checklist line and a CLAUDE.md paragraph are visibly
the same rule.

**Maintain a registry** in CLAUDE.md — id, one-line statement, path to the checking
script, and which of the four layers it actually has.

"Start empty" means empty of BORROWED rules — do not copy another project's, they
are domain-specific by construction and a checklist full of inapplicable rules
trains the agent to skim the ones that apply. It does NOT mean an empty table when
the project already has such rules: an existing check with layers 1, 2 and 4 but no
hook belongs in the registry on day one, with the missing layer named. An
unregistered rule is one nobody can see is half-built.

**A red check that gates nothing is worse than no check** — it looks like coverage
while providing none. If a check cannot be wired into a hook yet, say so where it
is defined and record why.

## Command routing

Before starting the setup workflow, check if the user is invoking a sub-command:

- **"Проведи дрейф-аудит" / "drift audit" / "дрейф аудит" / "сверь yaml с кодом"** → jump to "Drift Audit Workflow" section below, do NOT run setup steps
- **"Добавь фичу по AF" / "новая фича AF" / "implement feature AF" / "нужен ли ADR"** → jump to "Feature Workflow" section below, do NOT run setup steps
- **"Проверь Feature N" / "проверь фичу" / "review Feature" / "проверь выполненную задачу"** → jump to "Feature Review Workflow" section below, do NOT run setup steps
- **"обнови проект под AF" / "апгрейд AF" / "upgrade AF" / "обнови AF до текущей версии"** → jump to "Upgrade Workflow" section below. **This is NOT setup.** The project already has AF artifacts and some of them are worth more than what the templates carry — running setup over them destroys project-specific checks
- **Setup / migrate / "настрой AF"** → continue with workflow below

**Routing a request that mentions an existing AF project and a newer skill:** it is
an upgrade, not a setup. Setup's rule for a conflict is "overwrite"; upgrade's is
"merge". If a request is ambiguous, ask which one before touching a file.

## Workflow

### Step 1: Detect project state
- New project → follow "Чеклист старта на новом проекте" in guide.md
- Existing project, no AF artifacts → follow "Приложение Б" (migration) in guide.md
- **Existing project that ALREADY has `documentation/project.yaml`** → this is not a
  setup. Stop and switch to the **Upgrade Workflow**. Re-running setup over live AF
  artifacts overwrites the project's own checks

### Step 2: Gather context from user
REQUIRED before proceeding:
- Project stack (e.g. "FastAPI + React/Vite")
- Which layer to start with — pick the most-touched one, since its block boundaries
  are usually the most obvious. This is about sequencing, not about limiting scope:
  the remaining layers can follow in the same session once each one's cutting
  principle is agreed (see Critical rules).
- Path to feature/module folders (e.g. "src/features/" or "web/frontend/src/features/")

If user didn't provide these — ASK before scanning.

**Ask them in the language of the conversation.** The table below is reference
material, not a script to read out: quoting it verbatim asks a Russian-speaking
user four questions in English for no reason.

**Also ask these four — they decide which optional sections get generated.** Each
one, if generated blindly, either breaks the project or fills a mandatory checklist
with rules that do not apply. Noise in a mandatory checklist teaches the agent to
skim it, which costs more than the missing rule would have.

| Question | If yes | If no |
|---|---|---|
| **Deploy model** — does a push to the default branch deploy? | Branch + local merge, then push. Generate the `check-not-main` guard anyway — see below. Do NOT generate a PR gate | Branch + PR + review gate |
| **Database migrations?** | Generate the migration-integrity items in Self-Check and Feature Review (see the migration paragraph in Review step 5) | Omit them entirely |
| **Where do plans with acceptance criteria live?** Ask for the CONVENTION, not one filename — `documentation/*-plan.md`, `plan.md`, or "the file the task names". A dated one-off plan hardcoded into CLAUDE.md goes stale the moment the next plan appears | Generate a "Reading order" section pointing Review step 1 at that convention | Review step 1 falls back to step 3.5's criteria; if those are absent too, it says so rather than inventing them |
| **Startup checks needed** (Docker, tunnels, external services, seeded DB)? | Generate a "Session startup checks" section with the branches the user describes | Omit — a startup section listing nothing is worse than none |

Record the answers; they are also what a future agent needs in order to understand
why a section is present or absent.

**On `check-not-main` and deploy-from-main — a correction worth stating explicitly,
because the obvious guess is wrong.** The guard is a **pre-commit** hook: it refuses
`git commit` while HEAD is on the default branch. It is compatible with a
deploy-on-push setup, and the reasoning is mechanical:

- it never runs on `git push`, so it cannot block a deploy;
- with `branch → merge --ff-only → push` no commit is created on the default branch
  at all, so the hook does not fire once;
- and merges do not trigger it either — git invokes `pre-merge-commit` for those,
  not `pre-commit`, and the framework installs only `pre-commit` by default.

So the deploy-model answer decides the **PR gate**, not the branch guard. Generate
the guard for both models. What it buys, in either: the moment a task's first
`git commit` lands, being on the wrong branch stops being a judgement call.

### Step 3: Inventory (existing projects only)
- Scan the chosen layer's folder structure
- Propose block breakdown: list of blocks with code_path, entry, 1-line summary
- **STOP and present to user for approval** before creating manifest

### Step 4: Create structure
Copy and adapt templates to project:
- `templates/project.yaml` → `documentation/project.yaml` — keep `meta.af_version`
  and set it to the newest version in `CHANGELOG.md` next to this file. Dropping this field is
  not cosmetic: it is what a later Upgrade Workflow diffs against, and without it
  an upgrade cannot tell what to apply
- `templates/layer.yaml` → `documentation/<layer>.yaml` (filled with approved blocks)
- `templates/validate.py` → `documentation/validate.py` (adapt paths to project)
- `templates/check-claude-md-sections.py` → `documentation/check-claude-md-sections.py`
- `templates/check-adr-append-only.py` → `documentation/check-adr-append-only.py`
- `templates/check-gotcha-budget.py` → `documentation/check-gotcha-budget.py`
- `templates/check-not-main.py` → `scripts/check-not-main.py` (NOT into validate.sh — that script must stay runnable on the default branch)
- `templates/pre-commit-config.yaml` → `.pre-commit-config.yaml` (delete or enable the `check-not-main` hook per the deploy-model answer from Step 2)
- `templates/validate.sh` → `scripts/validate.sh`
- `templates/generate-manifest.py` → `documentation/generate-manifest.py` (optional, for 20+ blocks)
- `templates/yaml-to-mermaid.py` → `documentation/yaml-to-mermaid.py` (optional, on-demand graphs)
- `templates/ci-validate.yml` → `.github/workflows/validate-docs.yml` (optional, for teams)

### Step 5: Update project's CLAUDE.md
Target file: `CLAUDE.md` in the project root (NOT the skill's files).

**Behavior:**
- If CLAUDE.md exists: APPEND sections from `templates/claude-md-sections.md` at the end. Do NOT overwrite existing content. Do NOT duplicate sections if they already exist (check by heading text).
- If CLAUDE.md does NOT exist: create it with sections from the template.
- Preserve all existing user content, commands, and project-specific instructions.

**Sections to add:**
- `## Agent entry points` — tells future agents to start from project.yaml
- `## Task routing` — incl. Step 0 size check and the Self-Check checklist
- `## When refactoring` — enforces manifest updates
- `## Git workflow` — branch per task; merge model filled in from Step 2
- `## Agent autonomy rules` — Do/Ask/Never lists
- `## Project-specific rules (Hard Rules)` — empty registry, filled from this project's incidents
- `## Closed investigations` — empty, filled as questions get settled
- `## Self-maintaining documentation rules` — rules for auto-updating gotchas

Omit only the sections Step 2's answers rule out, and say which ones and why.

**Placement:** insert new sections near the top of CLAUDE.md (after the project overview but before detailed commands), so future agents see them early.

**After updating:** show user a diff of what was added and ask for confirmation before saving.

**Then run `python documentation/check-claude-md-sections.py`.** The approval step
above is where sections get lost — a long diff gets trimmed and nothing afterwards
notices. Do not skip this because the diff "looked complete"; that judgement is
exactly what the check exists to replace.

### Step 6: Verify
- Run `python documentation/validate.py` — must output "OK"
- Run `python documentation/check-claude-md-sections.py` — must output "OK". This is
  the step that catches a Step 5 diff that got trimmed during approval. **Do not
  report setup as complete while it exits non-zero**: report which sections are
  missing and either restore them or record why they are deliberately absent
- Tell user to run `pip install pre-commit && pre-commit install`
- Suggest user makes a test commit

## Critical rules

- **DO NOT manifest a layer before its cutting principle is agreed.** "Block = folder"
  is right when folders already carry clean boundaries. It is wrong where a folder
  glues unrelated modules together (a `lib/` holding SQLite, SMTP and pricing maths
  needs block = module) or where many thin routes share one renderer (that is one
  block, not N clones). Settle this per layer, with the user, before writing anything.
  Covering every layer in one session is fine once each principle is agreed — what is
  not fine is replicating a bad cut across layers.
- **DO NOT generate placeholder blocks.** A manifest full of `summary: TODO` is worse
  than no manifest: it looks like coverage without being coverage. If there is no time
  to write meaningful summaries for a layer, do not start that layer.
- **DO NOT create ADRs retrospectively** for past decisions
- **ALWAYS STOP for user input** at these points:
  - Choosing primary layer (if not provided)
  - Block boundaries and naming
  - Adapting template paths to project structure
- **DO NOT fill gotchas** — only user knows non-obvious footguns
- **DO NOT skip the inventory preview** — user must approve block breakdown before manifest is created

## When user's project has unusual structure

If feature folders don't exist (e.g. flat src/ with no features/ subfolder):
- Ask user how code is organized
- Propose manual block definition based on user's description
- DO NOT force src/features/ convention on projects that don't use it

## After setup is complete

Tell the user:
1. Run `pip install pre-commit && pre-commit install`
2. Run `python documentation/validate.py` to verify
3. Make a test commit to confirm pre-commit hook works
4. Refer to `guide.md` Appendix Д for day-to-day usage patterns
5. Extending to the remaining layers needs no waiting period. It needs one thing:
   the cutting principle for each new layer agreed first (see Critical rules).
   Extend as soon as that is settled — the same session is fine. What still has to
   be earned over real tasks is confidence that the manifest is *useful*: watch
   whether agents read the YAML or fall back to grepping, and enrich fields
   accordingly.
6. Optional tools available:
   - `python documentation/generate-manifest.py <dir>` — auto-generate skeleton manifest from directory (useful for 20+ blocks)
   - `python documentation/yaml-to-mermaid.py` — generate Mermaid dependency graph on demand
   - `.github/workflows/validate-docs.yml` — CI validation (copy from templates when
     working in a team). **This is not "CI" in the usual sense** — see below

### On CI: the template and a real pipeline are different things

`templates/ci-validate.yml` runs exactly one command — `python documentation/validate.py`
— on PRs touching `documentation/**` or `src/**`. Seconds, no dependency install,
no build. Cheap enough that it never becomes the thing you switch off.

A full pipeline — install, lint, typecheck, tests, migrations, build — is a
different decision with a different cost, and the skill does not ship one. Do not
read the optional template as a recommendation to build one.

**Where a full pipeline earns its keep, and where the clean-session review already
covers you:**

| Defect class | Full CI | Clean-session review |
|---|---|---|
| Uncommitted file, dependency missing from the manifest, env-dependent behaviour | catches it | **misses it by default** — same working tree; closed by the clean-checkout item in review step 5 |
| Breakage on a different OS or runtime version | catches it | misses it |
| False claim that a test protects something | misses it — every gate stays green | catches it (step 7) |
| Acceptance point silently unimplemented | misses it | catches it |
| Process rule violated | misses it | catches it (step 8) |

Reported from real use: a team ran both, found the full pipeline slow relative to
what it added on top of the review, and dropped it — keeping the review as the sole
gate. That is a defensible trade **provided** the clean-checkout item in step 5 is
actually done, because that is the one column the review would otherwise leave
empty.

Two things not to confuse with each other: a pipeline that *gates merges* and one
that *deploys*. Dropping the first says nothing about the second.

---

## Drift Audit Workflow

When user says "Проведи дрейф-аудит" / "drift audit" / similar — run semantic drift check between YAML manifests and real codebase.

`validate.py` only catches broken references (missing files/paths). Drift audit catches stale `summary`, outdated `notes`, missing file mentions, and semantic mismatches. Run periodically (every 2-4 weeks, or after major refactoring).

### Drift Audit Steps

1. **Locate manifests**
   - Read `documentation/project.yaml` to find all layer YAMLs
   - Load every layer YAML listed under `layers:`

2. **For each block in each layer:**
   - Read `code_path` folder and list actual files
   - Read `entry` file and 1-2 other key files (skim, don't read entirely if large)
   - Compare against YAML fields:
     - **summary** — does it still accurately describe what this block does?
     - **notes** — are mentioned files still present? any new important files missing from notes?
     - **gotchas** — are they still relevant, or does the code show they've been fixed?
     - **api_calls** (if present) — still accurate?
     - **depends_on** / **related_blocks** — still accurate?

3. **Output format: report-only, no edits**

   ```
   Drift Audit Report (documentation/<layer>.yaml)

   Block: <block-name>
     - [field]: [drift description] — [suggested fix]
     - [field]: [drift description] — [suggested fix]

   Block: <block-name>
     — no drift detected

   ...

   Summary: N blocks checked, M have drift, K clean.
   ```

4. **DO NOT auto-edit YAML** — wait for user confirmation
   - After report: ask "Какие правки применить? (все / список блоков / отмена)"
   - Apply only what user approves
   - After edits: run `python documentation/validate.py` to confirm still valid

### Critical rules for drift audit

- **Report-only mode** — NEVER edit YAML without explicit user approval
- **Don't be overly aggressive** — a block can intentionally have minimal notes; don't flag that as drift
- **Semantic mismatches are priority** — wrong summary is more important than missing file mention
- **If block has many files, skim key ones** — don't read 50 files exhaustively, sample wisely
- **Budget** — for each block, aim for 1-3 findings max; if finding more, re-check if standard is too strict

### What counts as drift (examples)

| Drift type | Example |
|---|---|
| Stale summary | Summary says "v1 RAG orchestrator" but code is clearly v2 now |
| Missing file in notes | notes lists old files but new `xyz_handler.py` is central and unmentioned |
| Dead file in notes | notes references `foo_service.py` that no longer exists in folder |
| Fixed gotcha | gotcha says "Don't do X — crashes on Y" but code now handles Y gracefully |
| Wrong dependency | `depends_on: [auth]` but block no longer imports anything from auth |

### What does NOT count as drift

- Minor wording improvements to summary (if meaning is same)
- Missing optional fields (empty `api_calls`, `gotchas`, etc. are fine)
- Small helper files not worth mentioning in notes
- Style/formatting preferences

---

## Upgrade Workflow

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
   - Read `CHANGELOG.md` **next to this file**, in the skill's own directory. It
     ships with the skill precisely so an upgrade works on any machine without
     knowing where the source archive lives. Every entry newer than the project's
     version is in scope.
   - If the project's version equals the skill's — say so and stop. Do not
     "refresh" files that are already current.
   - **If no CHANGELOG is reachable, stop and say so.** Guessing the delta by
     diffing files is how project-specific checks get deleted as "drift".

2. **Ask the setup questions the project never answered.** Later versions add
   questions to Step 2 that did not exist when this project was set up. Ask them
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

---

## Feature Workflow

Applies to ALL tasks automatically. Route by task type:

- **New feature / new module / bug fix (logic) / refactoring** → Full 9-step workflow below
- **Bug fix (trivial: typo, text, style)** → Light workflow: Orient → read gotchas → fix → commit
- When user explicitly says "добавь фичу по AF" / "implement feature AF" / "нужен ли ADR" → always full 9-step workflow

See `guide.md` Appendix Е for full reference.

### Step 0: Size check — does this fit in one reviewable unit?

Before orienting, check the task fits. The binding constraint is not "how long will
this take" — it is:

> **Can a reviewer agent, in a clean session with no implementation context, verify
> EVERY acceptance point of this task?**

If no → split before starting. A task too large to review is a task that never
closes: the Definition of Done never goes fully green, and the review either gets
skipped or degrades into skimming.

**Each part after splitting must have:**
- **One cognitively whole artifact** — one page, one endpoint group, one algorithm.
  Not "half of the auth system"
- **Its own acceptance criteria** — checkable independently
- **An explicit `Out of scope` list** — what this part deliberately does NOT do.
  This is the anti-scope-creep device; without it parts leak into each other
- **Declared dependencies and order** — what blocks what, what can run in parallel
- **Independently mergeable** — each part is a working state, not a half-migration

**Naming:** if the plan calls the whole thing Feature N, parts are N-a, N-b, N-c.
Keep the umbrella name in forward references so links from ADRs and manifests
don't break.

**Do not split** when the parts would leave the repo in a broken intermediate
state, or when a part has no acceptance criteria of its own. Then it is one task,
and the honest move is to say the review will need more than one session.

### Feature Workflow Steps (9 steps)

1. **Orient** — read `documentation/project.yaml` to find affected layers
2. **Read block context** — read YAML of affected blocks: summary, gotchas, notes, related_blocks. **Print all gotchas of affected blocks to the user** — this is mandatory, never skip silently
3. **Decide on ADR** — ask the 3-criteria question:
   - Are there 2+ reasonable ways to implement?
   - Would someone in 6 months ask "why X not Y?"
   - Did deciding take >10 minutes?
   - All YES → create ADR BEFORE implementation, link via `adr: [N]` in block
   - Any NO → skip ADR, just implement
3.5. **Fix the acceptance criteria — BEFORE writing anything.**
   - There is a plan → copy this task's criteria out of it verbatim.
   - There is no plan → write them yourself and show them to the user for
     confirmation, before the first line of code. Then put them where the reviewer
     will find them: the plan, the task description, or the commit body.

   **Scale them to the task.** A feature gets a list; a moved button gets one line
   — *"the Submit button now sits under the field, nothing else moved"* is a
   complete criterion: checkable, and possible to fail. There is no target count.

   **Never write criteria after the work.** Criteria derived from what was built
   describe the result instead of committing to it, and a review against them
   always passes. That is not a check, it is a transcript — the same defect class
   as claiming a test protects something because it was meant to.

   **Confirmed criteria are not edited to match the outcome.** If one turns out to
   be wrong or unreachable, say so explicitly and restate it *before* reviewing
   against it. Quietly aligning them with the code is a retroactive ADR rewrite by
   another name.

   Why before rather than after: it catches a misread task at the cheapest possible
   moment. "Fix the heading" understood as every page when one was meant shows up
   in a sentence, not after ten commits. If the user is unavailable, still write
   them down, marked as an assumption — a commitment made before the code is worth
   far more to a reviewer than one reconstructed after it.

   Skipped on the Light workflow (typo, copy, styling) — see Task routing.

4. **Confirm the APIs, then write tests** — in that order:
   - **4.0 — context7 gate, MANDATORY, before the first `Edit`/`Write` of the task.**
     List every external library this task will touch — framework, ORM, validation,
     **test runner, assertion and mocking libraries**, build tool, plugins. For each,
     resolve it and query current docs. The point is to confirm the APIs you are
     about to call still exist and are not deprecated in the major version this
     project pins. **Training data is not an acceptable source.** If an API cannot
     be confirmed in the docs — do not write anything; confirm it or escalate.
   - **4.1 — write tests** for key scenarios of the module, BEFORE implementation.
     Not per function — per module. Cover main success paths, edge cases, error
     handling.

   **The gate fires before the tests, not after.** Test files are code: they call
   the runner's API, the assertion API, the mocking API, and the API of the module
   under test. Tests written from memory fail for the wrong reason, and — worse —
   pin the implementation to an API that was imagined. Any workflow that numbers
   "write tests" ahead of the context7 gate contradicts itself, because writing a
   test IS the first `Write`.

   Why a gate and not a checklist item: a checkbox ticked after the fact costs
   nothing and gets ticked anyway. A gate before the first edit does not.
5. **Implement** — write the feature code, run tests. Green → continue. Red → fix → rerun
6. **Update YAML** for affected blocks if changed:
   - `code_path` / `entry` — if files moved
   - `summary` — if block purpose changed
   - `notes` — if key file added/removed
   - `api_calls` — if new endpoint
   - `depends_on` / `related_blocks` — if connections changed
7. **Add gotcha** — if stumbled on non-obvious issue (budget: 1-2 per session)
8. **Self-Check** — before committing, verify code against cross-cutting rules:
   - [ ] context7: **verify step 4.0 actually happened before the first `Edit`/`Write` — tests included** — this box is verification that the gate was passed, NOT a substitute for it. Ticking it post-hoc after writing code from memory is the failure mode this wording exists to prevent
   - [ ] sequential-thinking: **name the forks it was used on.** Reasoning done silently is unverifiable, and verifiability is the entire value of the rule. "Used it" with nothing to point at means it was not used
   - [ ] **Claims about your own work are verified, not intended.** For every statement that something is covered, protected, prevented or guaranteed by a test — did you watch that test go red with the protection removed? A tripwire that never fired documents the hazard; it does not guard against it. This is the one defect class no machine gate catches, which is why it is also a review item
   - [ ] KISS: no functions > 40 lines, no nesting > 3 levels?
   - [ ] DRY: grepped project for similar logic, no unnecessary duplication?
   - [ ] SOLID: each new module/class has single responsibility?
   - [ ] Feature-Based: new code is inside features/[name]/, not in root or wrong folder?
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
9. **Commit** — pre-commit hook validates references

### ADRs are append-only — except the `Affects:` index

"Append-only" applies to the **decision**: Context, Decision, Consequences,
alternatives. Those record what was decided and why, at a point in time. Editing
them later rewrites history; supersede with a new ADR instead.

`Affects:` is **not part of the decision**. It is a cross-reference index, and
`validate.py` check 4 requires it to list every block that declares `adr: [N]`. So
the moment a NEW block starts depending on an existing decision, that ADR's
`Affects:` line has to gain a name — and this is explicitly allowed, and needs no
permission. Adding a consumer to an index is not rewriting a decision.

**Without this carve-out the two rules contradict each other**, and an agent that
hits the contradiction resolves it by unblocking itself — which teaches it that
rules are negotiable when inconvenient. Observed exactly once, in a real session:
`validate.py` blocked the commit, the agent found a precedent for the same edit in
the ADR history and proceeded without asking.

Enforced by `check-adr-append-only.py`: modifications to an existing ADR are
rejected unless every changed line is the `Affects:` line.

### ADR Decision Rule (3 criteria)

Create ADR ONLY if all 3 are true:
1. Multiple reasonable implementation paths exist
2. >10 minutes spent on decision
3. Future "why X?" question is likely

### Examples: ADR needed or not?

| Feature | ADR? | Why |
|---|---|---|
| New endpoint following existing pattern | ❌ | Trivial, follows template |
| Bug fix in validator | ❌ | No alternatives |
| UI text change | ❌ | Trivial |
| WebSockets vs SSE for real-time | ✅ | Real alternatives exist |
| Keycloak vs self-hosted auth | ✅ | Major architectural choice |
| JSON fields vs normalized tables | ✅ | Trade-off decision |
| New LLM provider via factory | ⚠️ | Depends: follows pattern → no, changes pattern → yes |

### Critical rules for feature workflow

- **One task = one branch.** Create the branch BEFORE the first commit, never work
  directly on the default branch. Name it `<type>/<scope>-<slug>` mirroring the
  commit convention — `feat/f11a-taxonomies`, `fix/reviews-depth-bug`,
  `docs/seo-plan`. This is independent of whether the project uses pull requests:
  branching costs nothing on a solo repo and keeps an escape hatch when a task
  turns out wrong. Whether the branch then goes through a PR with a review gate,
  or is merged locally, is a per-project answer — see Step 2 of setup.
- **A task is not done until it has been reviewed in a clean session.** Run the
  Feature Review Workflow below before merging. Self-review by the agent that wrote
  the code is not a review — it is the same context grading its own work.
- **ADR BEFORE implementation, never after** — retrospective ADRs are forbidden
- **If you start coding and realize "this is a real choice"** — stop, write ADR, then continue
- **Update YAML as you go** — don't defer to "cleanup pass later"
- **Link ADR both ways** — block's `adr: [N]` + ADR's `Affects: [block-name]`
- **Show user the plan before coding** — especially when ADR is needed, let user approve the direction

### Output format for user

When routing to this workflow, present to user:
```
📋 AF Feature Workflow

Задача: <describe feature>

Шаг 1-2: Ориентирование
  Затронутые блоки: <list from YAML>

  Gotchas (обязательно прочитать):
    <block-name>:
      - <gotcha 1>
      - <gotcha 2>
    <block-name>: нет gotchas

Шаг 3: ADR analysis
  Варианты: <option A>, <option B>, ...
  Решение: <нужен ADR | не нужен, потому что...>

Если ADR нужен:
  Предлагаемый ADR: "ADR-NNN: <title>"
  Context: ...
  Decision: ...

Начинать реализацию? (yes / правки)
```

Wait for user approval before creating ADR and writing code.

---

## Feature Review Workflow

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
6. **Verify cross-cutting rules** (grep-based):
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
