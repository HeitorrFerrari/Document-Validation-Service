---
name: evaluation
description: Business rules, internal patterns, and communication contracts for the evaluation
  module. Load before working on any feature in app/evaluation.
---

# Module: evaluation

**Path:** `app/evaluation/`

## Responsibility

Harness de avaliação contínua/regressão do pipeline (Fase 10): roda `app_graph` contra o dataset
sintético de referência (`dataset.py`), compara score/elegibilidade com o esperado, e usa
`app/judge` como segunda checagem de consistência por caso. Serve de baseline antes de qualquer
ajuste de prompt — mede se mudou pra melhor ou pra pior, em vez de julgar no olho.

## Business Rules

- Cada `EvalCase` define uma faixa de score esperada (`score_esperado_min/max`), não um valor
  exato — score de LLM não é determinístico ponto a ponto, mas deve cair numa faixa plausível.
- Roda como script manual (`python -m app.evaluation.evaluation`), mesmo padrão de
  `app/tests/graph_tests/test_graph.py` — não é teste de CI, faz chamadas reais à API da OpenAI
  (6 casos × ~4 chamadas LLM cada: extração, validação, feedback, judge).

## Internal Patterns

**Structure:**
```
app/evaluation/
├── dataset.py       # EvalCase (dataclass) + DATASET: 6 pares currículo+vaga sintéticos
└── evaluation.py     # run_evaluation() -> compara app_graph+judge contra o dataset, imprime resumo
```

## Relationships

### Emits
Chamadas `trace("eval", ...)`.

### Consumes
`app_graph.invoke(...)` (`app/graph`), `judge.evaluate(...)` (`app/judge`).

### Depends On
`app/graph`, `app/judge`, `app/schemas`, `app/core/tracing`.

## Known Gotchas

Dataset é sintético (6 casos: match forte, match fraco, match parcial, duas bordas, sem
experiência) — cobre direção geral, não é golden dataset validado por um recrutador humano de
verdade. Rodar o harness custa ~24 chamadas de LLM por execução; não rodar em loop automatizado
sem necessidade.
