# Drift Audit Workflow

> Part of the `agent-first-setup` skill. Paths like `templates/…`, `guide.md`,
> `CHANGELOG.md` are relative to the skill root — the folder holding `SKILL.md`.


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
