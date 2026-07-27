---
name: graph
description: Business rules, internal patterns, and communication contracts for the graph
  module. Load before working on any feature in app/graph.
---

# Module: graph

**Path:** `app/graph/`

## Responsibility

Pipeline "oficial" de validação como grafo LangGraph (extract → validation → feedback), Fase 5.

## Business Rules

Nenhuma própria — orquestra `app/agents` e `app/api/extraction`, que carregam as regras.

## Internal Patterns

**Structure:**
```
app/graph/
└── graph.py   # extract_node, validation_node, feedback_node -> compilado como app_graph
```

## Relationships

### Emits
Nada.

### Consumes
`app/agents.validate_eligibility`, `app/agents.build_feedback`, `app/api/extraction.extrair_curriculo`.

### Depends On
`app/agents`, `app/api/extraction`, `app/states`.

## Known Gotchas

Nenhuma pendente. `app/worker/tasks.py::analisar_curriculo_task` agora invoca
`app_graph.invoke({...})` de verdade (decisão registrada em `DECISIONS.md`) — deixou de ser
código decorativo. `resume_id`/`job_id` do `ValidationResult` continuam sendo setados DEPOIS do
`.invoke()`, dentro da task, porque o grafo não tem esses valores no seu estado (só existem depois
da persistência no Mongo).
