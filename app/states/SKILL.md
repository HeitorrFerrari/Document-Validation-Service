---
name: states
description: Business rules, internal patterns, and communication contracts for the states
  module. Load before working on any feature in app/states.
---

# Module: states

**Path:** `app/states/`

## Responsibility

Definição TypedDict do estado do `app_graph` (LangGraph do pipeline principal). Estado do chat vive
separado, em `app/chats/chat_state.py`.

## Business Rules

Nenhuma — só definição de shape.

## Internal Patterns

**Structure:**
```
app/states/
└── state.py   # GraphState: resume_text, job_requirements, resume, validation, feedback
```

## Relationships

### Emits / Consumes
Nada.

### Depends On
`app/schemas` (CurriculoExtraido, ValidationResult, JobRequirements).

Usado por `app/graph/graph.py`.

## Known Gotchas

Nenhuma pendente. `need_more_infos` foi removido (era campo morto, vestígio de um fluxo abandonado
de "pedir mais informação ao candidato" junto com `app/tools/tools.py`, também removido) — decisão
registrada em `DECISIONS.md`.
