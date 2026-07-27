---
name: evaluation
description: Business rules, internal patterns, and communication contracts for the evaluation
  module. Load before working on any feature in app/evaluation.
---

# Module: evaluation

**Path:** `app/evaluation/`

## Responsibility

Harness de avaliação contínua/regressão do pipeline (Fase 10) — **ainda não implementado**.
Intenção documentada no próprio arquivo: rodar o pipeline (ou partes dele) contra um dataset de
referência e detectar regressão de qualidade entre mudanças.

## Business Rules

Nenhuma ainda — nada implementado.

## Internal Patterns

**Structure:**
```
app/evaluation/
└── evaluation.py   # só docstring, sem código
```

## Relationships

### Emits / Consumes / Depends On
Nenhuma ainda.

## Known Gotchas

Stub vazio. Antes de implementar, decidir a relação com `app/judge/` (ver `app/judge/SKILL.md`):
`judge` provavelmente é o crítico/scorer LLM-as-judge que roda em cada avaliação individual, e
`evaluation` é o harness que roda `judge` sobre um conjunto (dataset de currículos+vagas de
referência) e agrega/compara resultados entre execuções. Precisa de dataset de referência
(currículo + vaga + resultado esperado) que hoje não existe em lugar nenhum do repo.
