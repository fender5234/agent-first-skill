# AF Skill Improvement Plan

Based on analysis of 6 industry articles on agentic coding best practices (April 2026).

Sources:
- [CodeScene — Agentic AI Coding Best Practices](https://codescene.com/blog/agentic-ai-coding-best-practice-patterns-for-speed-with-quality)
- [Marmelab — Agent Experience: Best Practices](https://marmelab.com/blog/2026/01/21/agent-experience.html)
- [Aaron Gustafson — Optimizing Your Codebase for AI Agents](https://www.aaron-gustafson.com/notebook/optimizing-your-codebase-for-ai-coding-agents/)
- [Modern Descartes — Strategies for Working with Coding Agents](https://www.moderndescartes.com/essays/ai_codebase/)
- [Builder.io — AGENTS.md Tips](https://www.builder.io/blog/agents-md)
- [Stack Overflow — Coding Guidelines for AI and People](https://stackoverflow.blog/2026/03/26/coding-guidelines-for-ai-agents-and-people-too/)

Current coverage: ~14/20 recommendations (70%). Goal: 90%+.

---

## High Priority

- [ ] **Naming conventions** — add as cross-cutting rule 6
  - Explicit rules for naming: files, variables, functions, modules
  - Consistent naming = agent finds related code via grep
  - Without this, agent invents new names each time
  - Files: SKILL.md, guide.md, claude-md-sections.md, AGENTS.md
  - Also add naming check to Self-Check (step 8)

- [ ] **Security checklist** — add to Self-Check (step 8)
  - OWASP top-10 checks: SQL injection, XSS, secrets in code, unsafe dependencies
  - Agents generate vulnerabilities at speed — need explicit checklist
  - Files: SKILL.md (Self-Check section), guide.md (Appendix E), claude-md-sections.md, AGENTS.md

- [ ] **Explicit edge cases** — add documentation pattern
  - Document boundary conditions: null, empty arrays, timeouts, race conditions
  - Don't assume agent "understands" — make implicit knowledge explicit
  - Files: guide.md (new section or extend gotchas format)

## Medium Priority

- [ ] **Gold standard examples** — add example templates
  - Reference files showing correct project patterns
  - Agent copies style from examples better than following abstract rules
  - Before/after examples for anti-patterns
  - Files: templates/example-component/ (new directory with sample code)

- [ ] **AI-readiness assessment** — extend Step 1 (Detect project state)
  - Checklist before AF setup: function sizes, test coverage, documentation state, code health
  - If codebase is "dirty" — refactor first, then AF
  - Files: SKILL.md (Step 1), guide.md (new section before setup checklist)

- [ ] **YAGNI rule** — add to KISS section or as separate principle
  - Aggressively remove unnecessary features
  - Agent can easily add later — extra code now bloats context and confuses
  - "If feature is not needed right now — don't write it"
  - Files: SKILL.md, guide.md (extend KISS or add YAGNI sub-rule)

- [ ] **Anti-patterns with concrete examples** — add to guide.md
  - Specific bad code next to good code
  - Abstract "don't duplicate" is weaker than concrete diff "before -> after"
  - Files: guide.md (new section with code examples)

- [ ] **Feedback loop process** — add post-session workflow
  - Agent mistakes -> update rules/gotchas
  - If agent repeats same mistake -> add rule
  - Systematic process, not ad-hoc
  - Files: operator-guide.md, guide.md (new section "after session review")

## Low Priority

- [ ] **Code SEO / Searchability** — add to naming conventions or as separate tip
  - Synonyms in comments for better search
  - Unique file names (not 5 files named `index.ts`)
  - Full words instead of abbreviations
  - Files: guide.md (extend naming conventions section)

- [ ] **Visual/UI review** — add optional Self-Check section for frontend
  - UI verification via Playwright, screenshots, preview
  - Agent can't see rendered output — needs visual validation mechanism
  - Files: SKILL.md, claude-md-sections.md (optional frontend Self-Check)

- [ ] **Code health metrics** — integrate objective measurements
  - SonarQube, CodeScene, ESLint score integration
  - Numeric threshold instead of subjective "code is good"
  - Files: validate.py (extend) or CI pipeline template

- [ ] **Domain knowledge files** — add template
  - Separate .md files describing business domain: user personas, business rules, terminology
  - Agent understands "why" not just "how"
  - Files: templates/domain-glossary.md (new template)

---

## Progress

- Total items: 12
- Completed: 0
- Coverage after completion: ~95%
