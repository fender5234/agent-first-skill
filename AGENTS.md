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

### New feature / new module → Full 9-step workflow
1. Orient — read project.yaml, find affected blocks
2. Read block context — output gotchas to user (mandatory)
3. ADR decision — apply 3-criteria rule
4. Write tests — key scenarios per module, BEFORE implementation
5. Implement — with context7, sequential-thinking, KISS/DRY/SOLID/Feature-Based
6. Run tests — green → continue, red → fix
7. Update YAML — manifests of affected blocks
8. Self-Check — verify code against all cross-cutting rules (see checklist below)
9. Commit — pre-commit validates

### Self-Check checklist (step 8)
- [ ] context7: checked current docs for all libs/frameworks used?
- [ ] KISS: no functions > 40 lines, no nesting > 3 levels?
- [ ] DRY: grepped project for similar logic, no unnecessary duplication?
- [ ] SOLID: each new module/class has single responsibility?
- [ ] Feature-Based: new code inside features/[name]/, not in root or wrong folder?
- [ ] Feature-Based: no direct imports from another feature's internals (only via index.ts)?
- [ ] Feature-Based: nothing added to shared/ that's used by only 1 feature?
- [ ] Test-First: tests exist and pass for new/changed modules?
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

## Cross-cutting quality rules (apply to ALL stages)

### 1. Always use context7 for documentation
Before reading, writing, or reviewing any code — check current documentation via context7.
Applies to: frameworks, libraries, standard library of the language, build tools, test tools, CLI tools.
**Never rely on training data.** API changes between versions, best practices evolve, deprecated patterns persist in training data.

### 2. Always use sequential-thinking for structured reasoning
Before any non-trivial decision — use sequential-thinking.
Applies to: ADR decisions, choosing implementation approach, evaluating trade-offs, debugging complex issues, refactoring strategy.
Structure: problem → options → trade-offs → decision. Never "shoot from the hip."

### 3. Always apply KISS / DRY / SOLID when writing code
Apply during implementation, not as a separate review step:
- **KISS:** function > 40 lines → split; nesting > 3 levels → refactor
- **DRY:** grep project for similar logic before writing new code; 3 repetitions = abstraction threshold
- **SOLID:** single responsibility (S), extend don't modify (O), depend on abstractions (D)

### 4. Test-First at module level
- Write tests for key scenarios BEFORE implementation (per module, not per function)
- Implement → run tests → green = commit, red = fix
- Tests are the main safety net in agent-first — they verify behavior, YAML only verifies structure
- Register test commands in `project.yaml → tests`

### 5. Always use Feature-Based Architecture
- Structure: features/ (one folder per business capability) + shared/ (only code used by 2+ features)
- Colocation: components, hooks/services, types, tests — all inside the feature folder
- Features import each other only through index.ts (public API)
- Move to shared/ only when actually used in 2+ features, not preemptively
- Anti-pattern: layer-based grouping (controllers/, services/, models/)

## Agent autonomy rules

### Do without asking:
- Read code
- Run `scripts/validate.sh` or `python documentation/validate.py`
- Update YAML manifests after refactoring
- Create new ADRs when making architectural decisions

### Ask before:
- Deleting files
- Changing DB schema (migrations)
- Touching `.env` or config files
- Deploying to production
- Modifying existing ADRs (they are append-only)

### Never do:
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
├── project.yaml              ← super-index, entry point for agents
├── <layer>.yaml              ← blocks manifest per layer
├── validate.py               ← integrity checker
├── agent-first-guide.md      ← full methodology
└── adr/
    └── NNN-*.md              ← append-only decision records

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
