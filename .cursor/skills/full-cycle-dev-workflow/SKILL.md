---
name: full-cycle-dev-workflow
description: End-to-end software workflow for this repository—Think through Reflect, TDD and verification gates, review and ship. Use when starting features, planning architecture, debugging, reviewing code, testing, releasing, or when the user mentions brainstorming, plans, PR, ship, retro, or completion.
---

# Full-cycle dev workflow (project-local)

This skill encodes the seven-stage loop for **this project only** (`d:\transformer`). Stack here is **Python / PyTorch / ML**; React, Next.js, or PostgreSQL sections apply only when you touch those parts of the repo.

## Seven stages (summary)

1. **Think** — Validate ideas, explore requirements, challenge assumptions.
2. **Plan** — Written plans, architecture review, task breakdown.
3. **Build** — Prefer test-first or test-alongside for new logic; implement; debug systematically.
4. **Review** — Code and design review; security and data-safety mindset.
5. **Test** — Unit tests (pytest for Python), integration where needed; do not claim done without running checks.
6. **Ship** — PR hygiene, versioning mindset, release notes when applicable.
7. **Reflect** — Short retro: what broke, what to automate next.

## Think + Plan (equivalent skills)

| Name | When | Agent behavior |
|------|------|----------------|
| brainstorming | User says they want to build X | Clarify goals, constraints, success criteria; compare 2–3 approaches before coding. |
| office-hours | Early ideation | Stress-test whether the idea is worth the effort; list risks and unknowns. |
| writing-plans | Non-trivial or multi-step work | Produce a numbered plan with files/modules to touch and acceptance criteria. |
| plan-eng-review | Architecture or data-flow decisions | Review boundaries, data flow, failure modes, and edge cases before large edits. |
| dispatching-parallel-agents | Several independent subtasks | Split work into parallelizable chunks; avoid redundant file contention. |

## Build (equivalent skills)

| Name | When | Agent behavior |
|------|------|----------------|
| test-driven-development | **Before** adding non-trivial behavior | Prefer red–green–refactor: specify expected behavior (test or explicit checks), then implement. For this repo use **pytest** under relevant packages. |
| investigate | Bugs or regressions | Four-phase style: reproduce → narrow → root cause → fix + regression guard. |
| vercel-react-best-practices | React / Next.js files only | Apply performance and structure best practices when such files exist. |
| frontend-design + ui-ux-pro-max | UI work only | Consistent spacing, hierarchy, accessible contrast; avoid generic “AI slop” layouts. |
| postgresql-table-design | SQL / schema work only | Normalization, indexes, constraints, migration safety. |
| careful / freeze / guard | Destructive or prod-adjacent ops | Warn on deletes, mass refactors, credential changes, or unclear `rm`/migration commands. |

## Review + Test (equivalent skills)

| Name | When | Agent behavior |
|------|------|----------------|
| frontend-code-review | Front-end changes | Check structure, state, a11y basics, and bundle impact. |
| requesting / receiving-code-review | User asks for review or feedback | Give actionable review; if implementing feedback, re-verify behavior after changes. |
| design-review | Visual or UX changes | Check spacing, typographic hierarchy, and consistency with existing UI. |
| pytest | Python modules | Use fixtures, parametrization, and clear test names; run targeted tests after edits. |
| frontend-testing | JS/TS UI | Prefer Vitest + React Testing Library when that stack is present. |
| qa / webapp-testing | E2E or full flows | Describe critical user paths; suggest or run E2E when tooling exists. |
| verification-before-completion | **Always (mandatory)** | Do not say “done” without stating what was run (e.g. `pytest`, scripts, manual checks) and the outcome. |

## Ship + Reflect (equivalent skills)

| Name | When | Agent behavior |
|------|------|----------------|
| create-pr | Opening or describing a PR | Clear title, summary, test plan, and risk notes. |
| finishing-a-development-branch | Branch wrap-up | Merge or PR steps, cleanup temporary files, note follow-ups. |
| ship | Release mindset | Order: validate tests → review critical paths → version/changelog if releasing → PR. |
| document-release | After a release | Update README / CHANGELOG when the user ships a version. |
| retro | Periodic improvement | Summarize commits or recent work; note quality trends and one concrete improvement. |

## Automatic chain (mental model)

For a large feature request, prefer this order:

`brainstorming` → `writing-plans` → `test-driven-development` (or test-alongside) → `verification-before-completion` → `create-pr`.

## Project-specific defaults

- Default test runner: **pytest** for Python under this repo.
- ML training scripts: treat long runs as expensive; prefer small dry-run or unit tests over full training unless requested.
- Do not add dependencies to `requirements.txt` unless the user needs them.
