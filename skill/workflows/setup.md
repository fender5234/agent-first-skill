# Setup Workflow

> Part of the `agent-first-setup` skill. Paths like `templates/…`, `guide.md`,
> `CHANGELOG.md` are relative to the skill root — the folder holding `SKILL.md`.


### Step 1: Detect project state
- New project → follow "Чеклист старта на новом проекте" in guide.md
- Existing project, no AF artifacts → follow "Приложение Б" (migration) in guide.md
- **Existing project that ALREADY has `documentation/project.yaml`** → this is not a
  setup. Stop and switch to the **Upgrade Workflow** (`workflows/upgrade.md`). Re-running setup over live AF
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
| **Database migrations?** | Generate the migration-integrity items in Self-Check and Feature Review (see the migration paragraph in Review step 5, `workflows/review.md`) | Omit them entirely |
| **Where do plans with acceptance criteria live?** Ask for the CONVENTION, not one filename — `documentation/*-plan.md`, `plan.md`, or "the file the task names". A dated one-off plan hardcoded into CLAUDE.md goes stale the moment the next plan appears | Generate a "Reading order" section pointing Review step 1 (`workflows/review.md`) at that convention | Review step 1 falls back to the criteria from Feature step 3.5 (`workflows/feature.md`); if those are absent too, it says so rather than inventing them |
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
  and set it to the newest version in `CHANGELOG.md` in the skill root (next to `SKILL.md`). Dropping this field is
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
| Uncommitted file, dependency missing from the manifest, env-dependent behaviour | catches it | **misses it by default** — same working tree; closed by the clean-checkout item in review step 5 (`workflows/review.md`) |
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
