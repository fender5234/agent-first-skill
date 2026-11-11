# Cross-cutting rules (apply to ALL workflows)

> Part of the `agent-first-setup` skill. Paths like `templates/…`, `guide.md`,
> `CHANGELOG.md` are relative to the skill root — the folder holding `SKILL.md`.


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
