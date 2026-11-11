# Feature Workflow

> Part of the `agent-first-setup` skill. Paths like `templates/…`, `guide.md`,
> `CHANGELOG.md` are relative to the skill root — the folder holding `SKILL.md`.


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
8. **Self-Check** — before committing, verify code against cross-cutting rules (`rules/quality.md`):
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
  or is merged locally, is a per-project answer — see Step 2 of setup (`workflows/setup.md`).
- **A task is not done until it has been reviewed in a clean session.** Run the
  Feature Review Workflow (`workflows/review.md`) before merging. Self-review by the agent that wrote
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
