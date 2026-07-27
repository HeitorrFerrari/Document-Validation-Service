---
name: spec-driven-development
description: Use when starting any feature, fix, or change in {PROJECT_NAME}. Spec-first, TDD with
  immutable phase-1 tests, adapted to this project's stack ({FRAMEWORK}) and conventions. Auto-sizes
  depth by scope (quick fix vs full feature). Triggers on "specify", "design", "tasks", "implement",
  "build", "quick fix".
---

# Spec-Driven Development — {PROJECT_NAME}

Plan and implement features with precision, adapted to this project.

## Before any code

1. **Load context** — read `skills/project-context/SKILL.md` (domain, conventions, module map).
2. **Read the module** — open the affected `<module>/SKILL.md` (and submodule skill if relevant).
3. **Conventions** — read `references/project-conventions.md` for this project's stack and patterns.

## TDD is mandatory — immutable phase-1 tests

Read `references/tdd-immutable.md`. Tests are written FIRST as the frozen contract. Implementation
conforms to the tests. **Tests are never edited to make code pass.**

## Workflow

Follow the four adaptive phases below (cloned from tlc-spec-driven, stack-agnostic):
SPECIFY → DESIGN → TASKS → EXECUTE, auto-sized by scope. The remainder of this file and the
`references/` directory are the full workflow.

<!-- The cloned tlc-spec-driven body continues below this header when generated. -->
