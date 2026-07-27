# Attribution

`spec-driven-development` is derived from **tlc-spec-driven** (Tech Lead's Club — Spec-Driven
Development) by Felipe Rodrigues — https://github.com/felipfr — licensed CC-BY-4.0.

## Changes made by cast-skills

Per CC-BY-4.0, modifications are disclosed here.

**Modified — `SKILL.md` body** (changes marked inline with `[cast-skills]`):
- **Workflow** gained a "Step 0 — load project context" before every cycle.
- **Context Loading Strategy** adds `project-context/SKILL.md` to the base load and the affected
  `<module>/SKILL.md` to the on-demand load.
- **Auto-sizing rules** add an immutable test-first rule to the Execute phase.

All other `references/*.md` from tlc-spec-driven are bundled unmodified.

**Added — new files** (MIT-licensed, not part of the original work):
- `references/project-context-template.md` — generates per-project domain/stack context skills
- `references/module-template.md` — generates per-module business-rules skills
- `references/sdd-skill-template.md` — the project-adapted SDD SKILL.md header
- `references/tdd-immutable.md` — immutable phase-1 TDD contract (tests written first, never edited to pass)

Original tlc-spec-driven content remains CC-BY-4.0; cast-skills additions are MIT.
