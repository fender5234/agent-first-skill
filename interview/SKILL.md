---
name: interview
description: Interview the user about their project idea, ask deep questions about business requirements, technical decisions, and UI/UX, then generate a structured implementation plan ready for AF workflow execution. Use when user says "interview", "давай обсудим проект", "помоги спланировать", "нужен план", "plan the project", "let's plan".
---

# Interview → Project Plan

Structured interview that produces an implementation plan ready for AF 9-step workflow execution.

## Input detection

- **User describes idea in chat** (main scenario) → start Phase 1 immediately
- **User points to a file** (requirements.md, brief) → read file first, then start Phase 1 to fill gaps

## Phase 1: Interview (ask until complete)

Use AskUserQuestion tool. Ask deep, non-obvious questions. Do NOT stop after 2-3 questions — continue until you have full understanding.

### Business questions:
- What is the product? Who are the users?
- What are the key user scenarios (user stories)?
- What is MVP vs nice-to-have? What can be deferred?
- Are there competitors or reference products?
- Any deadlines or constraints?

### Technical questions:
- New project or existing codebase?
- Stack preferences? (if none — propose and justify)
- External integrations? (APIs, databases, auth providers, payment, etc.)
- Non-functional requirements? (performance, security, scalability)
- Deployment target? (Vercel, VPS, Docker, etc.)

### UI/UX questions:
- Are there mockups or designs? (Figma, sketches, reference sites)
- What are the main screens/pages?
- Responsive design needed?
- Any branding or style preferences?

### Rules for interviewing:
- Ask 2-4 questions at a time (not all at once — overwhelming)
- Skip questions that are already answered from user's initial description
- Go deeper on vague answers — "what exactly do you mean by..."
- If user says "you decide" — propose an option with justification, ask for confirmation
- Continue until ALL categories above are covered

## Phase 2: Generate plan

After interview is complete, generate the plan file at `documentation/plan.md` in the project root.

### Plan format (strict):

```markdown
# Project Plan: [project name]

## Overview
[1-2 sentences describing the project and its purpose]

## Stack
- Frontend: [framework + key libraries]
- Backend: [framework + key libraries]
- Database: [type + provider]
- Auth: [approach]
- Deployment: [target]

Stack justification: [why this stack — this becomes ADR-001 candidate during AF setup]

## Architecture
- Pattern: Feature-Based (modular)
- Frontend structure: src/features/
- Backend structure: app/features/ (or app/modules/)
- Shared code: src/shared/ (or app/shared/)

## Features (in implementation order)

### Feature 1: [name]
- **Description:** [what it does, 1-2 sentences]
- **Dependencies:** none
- **Acceptance criteria:**
  - [ ] [specific, testable criterion]
  - [ ] [specific, testable criterion]
- **Complexity:** low | medium | high

### Feature 2: [name]
- **Description:** [what it does]
- **Dependencies:** Feature 1
- **Acceptance criteria:**
  - [ ] ...
- **Complexity:** low | medium | high

[...continue for all features...]

## Milestones
- [ ] **Milestone 1:** [description] — after Features 1-N (first working version)
- [ ] **Milestone 2:** [description] — after Features N-M
- [ ] **Milestone 3: MVP complete** — after all features

## Out of scope (deferred)
- [feature or requirement explicitly postponed]
- [...]

## Open questions
- [anything unresolved that needs decision later]
```

### Rules for plan generation:
- Features ordered by dependencies — independent features first
- Each feature = one AF 9-step workflow iteration = one commit
- Features should be small enough to implement in one session
- If a feature is too big — split into sub-features
- Acceptance criteria must be specific and testable (not "works well")
- Complexity estimate helps user prioritize and plan time

## Phase 3: Review with user

After generating the plan, present it and ask:
1. Does this cover everything from your requirements?
2. Is the implementation order correct?
3. Should anything be added, removed, or reprioritized?
4. Are the acceptance criteria clear enough?

Apply corrections. Save final version to `documentation/plan.md`.

## After interview is complete

Tell the user:
1. Plan is saved to `documentation/plan.md`
2. Next step: run `/agent-first-setup` to create YAML manifests and project structure
3. Then execute features one by one through AF 9-step workflow
4. Each feature = one commit, review in separate window after each

## Critical rules

- **DO NOT skip the interview** — even if user gave detailed description, verify understanding
- **DO NOT generate plan without user confirmation** — always review in Phase 3
- **DO NOT combine multiple features into one** — each feature must be atomic (one commit)
- **DO NOT leave acceptance criteria vague** — "it should work" is not a criterion
- **DO NOT propose architecture without justification** — every choice needs a "why"
- **If user says "I don't know"** — propose options with trade-offs, let them choose
