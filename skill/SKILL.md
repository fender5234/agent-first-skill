---
name: agent-first-setup
description: Set up or migrate a project to agent-first architecture with YAML manifests, ADRs, validation, and pre-commit hooks. Also runs drift-audit to verify YAML manifests match reality, upgrades a project already on AF to a newer methodology version (merging, never overwriting its own checks), guides feature-implementation workflow (when to create ADRs, which YAML fields to update), and provides independent feature review in clean sessions. Use when user mentions "AF" (shorthand for agent-first), or asks to "setup agent-first", "make project agent-friendly", "add YAML manifests", "organize project for AI agents", "внедри agent-first", "настрой проект под агентов", "agent-first подход", "используй AF", "примени AF", "настрой AF", "проведи дрейф-аудит", "drift audit", "дрейф аудит", "проверь соответствие yaml коду", "сверь манифесты с кодом", "обнови проект под AF", "обнови проект под новый скилл", "апгрейд AF", "upgrade AF", "обнови AF до текущей версии", "перенеси изменения скилла в проект", "добавь фичу по AF", "новая фича AF", "implement feature AF", "AF workflow", "нужен ли ADR", "do I need ADR", "проверь Feature", "проверь фичу", "review Feature", "проверь выполненную задачу"
---

# Agent-First Project Setup

Methodology for organizing projects for AI-agent-driven development and maintenance.

## How this skill is organized — read this first

This file is only a router. Each workflow lives in its own file under `workflows/`,
and the shared rules under `rules/`. **Identify the command, then Read the file(s)
in the "Read before step 1" column BEFORE taking the first step. Do not run a
workflow from memory or from this table** — the steps, gates and critical rules
are in those files and nowhere else.

All paths below are relative to this skill's folder (the one holding `SKILL.md`).

## Command routing

| User says | Workflow | Read before step 1 |
|---|---|---|
| "Проведи дрейф-аудит" / "drift audit" / "дрейф аудит" / "сверь yaml с кодом" | Drift audit — do NOT run setup steps | `workflows/drift-audit.md` + `rules/quality.md` |
| "Добавь фичу по AF" / "новая фича AF" / "implement feature AF" / "нужен ли ADR" — **and any feature, logic bug fix or refactoring task in an AF project** | Feature — do NOT run setup steps | `workflows/feature.md` + `rules/quality.md` |
| "Проверь Feature N" / "проверь фичу" / "review Feature" / "проверь выполненную задачу" | Feature review — do NOT run setup steps | `workflows/review.md` + `rules/quality.md` |
| "обнови проект под AF" / "апгрейд AF" / "upgrade AF" / "обнови AF до текущей версии" | Upgrade. **This is NOT setup.** The project already has AF artifacts and some of them are worth more than what the templates carry — running setup over them destroys project-specific checks | `workflows/upgrade.md` + Step 2 of `workflows/setup.md` |
| Setup / migrate / "настрой AF" | Setup | `workflows/setup.md` + `rules/hard-rules.md` |

**Routing a request that mentions an existing AF project and a newer skill:** it is
an upgrade, not a setup. Setup's rule for a conflict is "overwrite"; upgrade's is
"merge". If a request is ambiguous, ask which one before touching a file.

A request that is setup by wording but the project ALREADY has
`documentation/project.yaml` is an upgrade — see Step 1 of `workflows/setup.md`.

## Files

- `workflows/setup.md` — setup / migration of a project, CI notes
- `workflows/upgrade.md` — upgrade a project already on AF (merge, never overwrite)
- `workflows/feature.md` — feature workflow: size check, 9 steps, ADR rules, Self-Check
- `workflows/review.md` — clean-session feature review (the merge gate)
- `workflows/drift-audit.md` — semantic check of YAML manifests against code
- `rules/quality.md` — the seven cross-cutting rules (context7, sequential-thinking,
  KISS/DRY/SOLID, Test-First, Feature-Based, Naming, Security)
- `rules/hard-rules.md` — the four-layer pattern for project-specific rules
- `CHANGELOG.md` — what changed between methodology versions; the Upgrade Workflow
  diffs a project's `meta.af_version` against it
- `guide.md` — full methodology and rationale, in Russian, for humans and as a
  reference. **Do not read it by default.** Read only the section a workflow file
  points to (e.g. "Приложение Б" for migration)
- `operator-guide.md` — for the human operator: how to give tasks and where the
  control points are. Read it only when the user asks how to work with the agent

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
