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

### New feature / new module → Full 8-step workflow
1. Orient — read project.yaml, find affected blocks
2. Read block context — output gotchas to user (mandatory)
3. ADR decision — apply 3-criteria rule
4. Write tests — key scenarios per module, BEFORE implementation
5. Implement — with context7, sequential-thinking, KISS/DRY/SOLID
6. Run tests — green → continue, red → fix
7. Update YAML — manifests of affected blocks
8. Commit — pre-commit validates

### Bug fix (logic/behavior) → Full 8-step workflow
Same as above. ADR will likely be "not needed" (step 3), but tests are mandatory — to prevent the bug from returning. Add gotcha describing the bug if non-obvious.

### Bug fix (trivial: typo, text, style) → Light workflow
1. Orient — read project.yaml, find affected block
2. Read block context — check gotchas
3. Fix
4. Commit — pre-commit validates

No tests, no ADR, no YAML update needed for trivial fixes.

### Refactoring → Full 8-step workflow
Tests are critical — they prove behavior is preserved. YAML update is mandatory since paths/structure likely change.

This routing applies to ALL tasks automatically, not only when user says "AF".

## Agent autonomy rules

### Do without asking:
- Read code
- Run `scripts/validate.sh`
- Update YAML manifests after refactoring
- Create new ADRs when making decisions

### Ask before:
- Deleting files
- Changing DB schema (migrations)
- Touching .env or config
- Deploying to production
- Modifying existing ADRs (they are append-only)

### Never do:
- push --force
- Commit secrets / .env
- Modify ADRs retroactively (create new one with "supersedes N")

## Cross-cutting quality rules

### 1. Always use context7 for documentation
Before reading, writing, or reviewing any code — check current documentation via context7.
Applies to: frameworks, libraries, standard library, build/test tools.
Never rely on training data — API and best practices change between versions.

### 2. Always use sequential-thinking for decisions
Before any non-trivial decision — use sequential-thinking.
Applies to: ADR decisions, implementation approach, trade-offs, debugging, refactoring.
Structure: problem → options → trade-offs → decision.

### 3. Always apply KISS / DRY / SOLID when writing code
- KISS: function > 40 lines → split; nesting > 3 levels → refactor
- DRY: grep project for similar logic before writing new code; 3 repetitions = abstraction threshold
- SOLID: single responsibility (S), extend don't modify (O), depend on abstractions (D)

### 4. Test-First at module level
- Write tests for key scenarios BEFORE implementation (per module, not per function)
- Implement → run tests → green = commit, red = fix
- Tests are the main safety net — they verify behavior, YAML only verifies structure

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
