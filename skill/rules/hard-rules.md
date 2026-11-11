# Project-specific rules — the Hard Rules pattern

> Part of the `agent-first-setup` skill. Paths like `templates/…`, `guide.md`,
> `CHANGELOG.md` are relative to the skill root — the folder holding `SKILL.md`.


The seven rules in `rules/quality.md` are universal. Every real project also accumulates rules that
are true only for it: "in this codebase, never call X directly — it deadlocks",
"every schema change needs a migration file in the same commit". These are the ones
that actually cause outages, and prose in CLAUDE.md does not hold them.

**A project rule is not finished until it has all four of these:**

| Layer | What it is | Why it alone is not enough |
|---|---|---|
| 1. **Statement** | one line in CLAUDE.md: "Don't X — it causes Y" | Prose is skippable. Agents read past it under load |
| 2. **Executable check** | a grep or a script that exits non-zero on violation | Without a machine check, compliance is self-reported |
| 3. **Pre-commit hook** | the check wired into `.pre-commit-config.yaml`, scoped by `files:` to the paths it applies to | An unwired script rots. It goes red and nobody notices |
| 4. **Review checklist item** | the same check named in the Feature Review Workflow (`workflows/review.md`) | Pre-commit can be bypassed with `--no-verify`; the clean-session review cannot |

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
