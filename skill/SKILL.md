---
name: agent-first-setup
description: Set up or migrate a project to agent-first architecture with YAML manifests, ADRs, validation, and pre-commit hooks. Also runs drift-audit to verify YAML manifests match reality, and guides feature-implementation workflow (when to create ADRs, which YAML fields to update). Use when user mentions "AF" (shorthand for agent-first), or asks to "setup agent-first", "make project agent-friendly", "add YAML manifests", "organize project for AI agents", "внедри agent-first", "настрой проект под агентов", "agent-first подход", "используй AF", "примени AF", "настрой AF", "проведи дрейф-аудит", "drift audit", "дрейф аудит", "проверь соответствие yaml коду", "сверь манифесты с кодом", "добавь фичу по AF", "новая фича AF", "implement feature AF", "AF workflow", "нужен ли ADR", "do I need ADR"
---

# Agent-First Project Setup

Methodology for organizing projects for AI-agent-driven development and maintenance.

## Full reference
Read `guide.md` for complete methodology, principles, and rationale.

## Templates (ready to copy)
- `templates/project.yaml` — super-index for the project
- `templates/layer.yaml` — blocks manifest template
- `templates/validate.py` — integrity checker (paths, ADR cross-refs, orphan detection)
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
Before any non-trivial decision — use sequential-thinking MCP server.
This applies to: ADR decisions, choosing implementation approach, evaluating trade-offs, debugging complex issues, refactoring strategy.
**Never "shoot from the hip."** Structure your reasoning: problem → options → trade-offs → decision.

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

## Command routing

Before starting the setup workflow, check if the user is invoking a sub-command:

- **"Проведи дрейф-аудит" / "drift audit" / "дрейф аудит" / "сверь yaml с кодом"** → jump to "Drift Audit Workflow" section below, do NOT run setup steps
- **"Добавь фичу по AF" / "новая фича AF" / "implement feature AF" / "нужен ли ADR"** → jump to "Feature Workflow" section below, do NOT run setup steps
- **Setup / migrate / "настрой AF"** → continue with workflow below

## Workflow

### Step 1: Detect project state
- New project → follow "Чеклист старта на новом проекте" in guide.md
- Existing project → follow "Приложение Б" (migration) in guide.md

### Step 2: Gather context from user
REQUIRED before proceeding:
- Project stack (e.g. "FastAPI + React/Vite")
- Primary layer to start with (ONE layer, not all)
- Path to feature/module folders (e.g. "src/features/" or "web/frontend/src/features/")

If user didn't provide these — ASK before scanning.

### Step 3: Inventory (existing projects only)
- Scan the chosen layer's folder structure
- Propose block breakdown: list of blocks with code_path, entry, 1-line summary
- **STOP and present to user for approval** before creating manifest

### Step 4: Create structure
Copy and adapt templates to project:
- `templates/project.yaml` → `documentation/project.yaml`
- `templates/layer.yaml` → `documentation/<layer>.yaml` (filled with approved blocks)
- `templates/validate.py` → `documentation/validate.py` (adapt paths to project)
- `templates/pre-commit-config.yaml` → `.pre-commit-config.yaml`
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
- `## When refactoring` — enforces manifest updates
- `## Agent autonomy rules` — Do/Ask/Never lists
- `## Self-maintaining documentation rules` — rules for auto-updating gotchas

**Placement:** insert new sections near the top of CLAUDE.md (after the project overview but before detailed commands), so future agents see them early.

**After updating:** show user a diff of what was added and ask for confirmation before saving.

### Step 6: Verify
- Run `python documentation/validate.py` — must output "OK"
- Tell user to run `pip install pre-commit && pre-commit install`
- Suggest user makes a test commit

## Critical rules

- **DO NOT document everything at once** — start with ONE layer
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
5. DO NOT extend to other layers for 1-2 weeks — observe if current setup works
6. Optional tools available:
   - `python documentation/generate-manifest.py <dir>` — auto-generate skeleton manifest from directory (useful for 20+ blocks)
   - `python documentation/yaml-to-mermaid.py` — generate Mermaid dependency graph on demand
   - `.github/workflows/validate-docs.yml` — CI validation (copy from templates when working in a team)

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

## Feature Workflow

Applies to ALL tasks automatically. Route by task type:

- **New feature / new module / bug fix (logic) / refactoring** → Full 9-step workflow below
- **Bug fix (trivial: typo, text, style)** → Light workflow: Orient → read gotchas → fix → commit
- When user explicitly says "добавь фичу по AF" / "implement feature AF" / "нужен ли ADR" → always full 9-step workflow

See `guide.md` Appendix Е for full reference.

### Feature Workflow Steps (9 steps)

1. **Orient** — read `documentation/project.yaml` to find affected layers
2. **Read block context** — read YAML of affected blocks: summary, gotchas, notes, related_blocks. **Print all gotchas of affected blocks to the user** — this is mandatory, never skip silently
3. **Decide on ADR** — ask the 3-criteria question:
   - Are there 2+ reasonable ways to implement?
   - Would someone in 6 months ask "why X not Y?"
   - Did deciding take >10 minutes?
   - All YES → create ADR BEFORE implementation, link via `adr: [N]` in block
   - Any NO → skip ADR, just implement
4. **Write tests** — write tests for key scenarios of the module BEFORE implementation. Not per function — per module. Cover main success paths, edge cases, error handling
5. **Implement** — write the feature code, run tests. Green → continue. Red → fix → rerun
6. **Update YAML** for affected blocks if changed:
   - `code_path` / `entry` — if files moved
   - `summary` — if block purpose changed
   - `notes` — if key file added/removed
   - `api_calls` — if new endpoint
   - `depends_on` / `related_blocks` — if connections changed
7. **Add gotcha** — if stumbled on non-obvious issue (budget: 1-2 per session)
8. **Self-Check** — before committing, verify code against cross-cutting rules:
   - [ ] context7: checked current docs for all libs/frameworks used?
   - [ ] KISS: no functions > 40 lines, no nesting > 3 levels?
   - [ ] DRY: grepped project for similar logic, no unnecessary duplication?
   - [ ] SOLID: each new module/class has single responsibility?
   - [ ] Feature-Based: new code is inside features/[name]/, not in root or wrong folder?
   - [ ] Feature-Based: no direct imports from another feature's internals (only via index.ts)?
   - [ ] Feature-Based: nothing added to shared/ that's used by only 1 feature?
   - [ ] Test-First: tests exist and pass for new/changed modules?
   If any check fails — fix before committing.
9. **Commit** — pre-commit hook validates references

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
