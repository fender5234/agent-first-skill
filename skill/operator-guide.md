# Operator Guide — Agent-First Workflow

How to work with an AI agent in an agent-first project.

---

## Your role

**You are the architect. The agent is the implementer.**

You decide "what" and "why". The agent decides "how" — guided by manifests, documentation (context7), structured reasoning (sequential-thinking), and code quality principles (KISS/DRY/SOLID).

---

## How to give tasks

### Good (outcome-level)
- "Add bot filtering by status"
- "Users complain that page loads slowly — investigate and fix"
- "We need WebSocket support for real-time updates"

### Bad (implementation-level)
- "Create a function filterBots that takes an array and returns filtered results"
- "Add useEffect in BotsList.tsx on line 42"

Why: the agent has full project context from YAML manifests. When you describe the outcome, the agent finds the right blocks, reads gotchas, checks documentation, and chooses the best approach. When you dictate implementation, the agent skips all of that.

---

## Interaction points

| Stage | What you do | What the agent does |
|---|---|---|
| **Task** | Describe outcome + why it matters | — |
| **Orientation** | Verify the agent found the right blocks. Read the gotchas the agent outputs | Reads project.yaml → layer.yaml → outputs gotchas |
| **ADR decision** | Approve or adjust the decision. Ask "what alternatives did you consider?" | Uses sequential-thinking to analyze options, presents trade-offs |
| **Implementation** | Don't intervene unless you see a problem | Checks docs via context7, writes code with KISS/DRY/SOLID |
| **Review** | Read the diff. Ask questions if something looks wrong | Presents changes, updates YAML |
| **Commit** | Confirm | Commits, pre-commit validates |

---

## When to say "stop"

- The agent picked the wrong blocks — "stop, this feature is in block X, not Y"
- The agent is overcomplicating — "this should be simpler, do we really need X?"
- The agent skipped gotchas — "what are the gotchas for this block?"
- The agent made an architectural choice without ADR — "this looks like a decision that needs an ADR"
- The agent is writing code without checking docs — "did you check context7 for the current API?"

Stopping early is cheap. Fixing after implementation is expensive.

---

## After each session

Ask yourself:

1. **Did I discover a non-obvious pitfall?** → Tell the agent to add it to gotchas
2. **Did the agent make a mistake that future agents would repeat?** → Add gotcha
3. **Did I make an architectural decision during the session?** → Should it be an ADR?
4. **Is the manifest still accurate after changes?** → Agent should have updated it, but verify

---

## Common mistakes

| Mistake | Why it's bad | What to do instead |
|---|---|---|
| Dictating implementation details | Agent skips orientation, context7, structured thinking | Describe the outcome |
| Ignoring gotchas output | You miss known pitfalls, waste time on known issues | Always read them |
| Saying "just do it" to ADR question | Skips structured decision-making, no record for future | Take 2 minutes to review the options |
| Not adding gotchas after finding issues | Next session (yours or someone else's) hits the same problem | Spend 30 seconds adding a one-liner |
| Expanding to all layers immediately | Manifests become stale because too much to maintain | One layer at a time, expand after 1-2 weeks |

---

## Quick reference

```
Start task → agent reads manifests → outputs gotchas → you verify
  ↓
Agent analyzes approach (sequential-thinking) → presents plan → you approve
  ↓
Agent checks docs (context7) → writes code (KISS/DRY/SOLID) → you review diff
  ↓
Agent updates YAML → commits → pre-commit validates → done
```
