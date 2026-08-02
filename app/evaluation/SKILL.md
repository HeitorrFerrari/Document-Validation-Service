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
- Nota por caso é 0-10, composta de 3 critérios binários com peso: `score_ok` (4 pontos),
  `elegibilidade_ok` (4 pontos), `judge_consistente` (2 pontos). `NOTA_CORTE = 7.5` — repare que
  isso exige `score_ok` E `elegibilidade_ok` juntos pra passar (8/10); o judge sozinho nunca salva
  um caso que errou o core (score+elegibilidade).
- Resultado persiste em JSON (`app/evaluation/results/eval_<timestamp>.json`), não no Mongo — é
  artefato de execução do harness, não dado de produto. Pasta gitignored.
- Roda de duas formas: script manual (`python -m app.evaluation.evaluation`, mesmo padrão de
  `app/tests/graph_tests/test_graph.py`) ou via `POST /evaluation/run` (`app/api/routes/evaluation.py`).
  Nenhuma das duas é teste de CI — fazem chamadas reais à API da OpenAI (6 casos × ~4 chamadas LLM
  cada: extração, validação, feedback, judge).

## Internal Patterns

**Structure:**
```
app/evaluation/
├── dataset.py       # EvalCase (dataclass) + DATASET: 6 pares currículo+vaga sintéticos
├── evaluation.py     # run_evaluation() -> EvalRunResult; salvar_resultado() -> grava JSON
└── results/           # gitignored -- JSON por execução, criado em runtime
```

## Relationships

### Emits
Chamadas `trace("eval", ...)`. Arquivo JSON em `results/` por execução.

### Consumes
`app_graph.invoke(...)` (`app/graph`), `judge.evaluate(...)` (`app/judge`).

### Depends On
`app/graph`, `app/judge`, `app/schemas` (`EvalCaseResult`/`EvalRunResult`, `ValidationResult`,
`JudgeResult`), `app/core/tracing`.

Consumido por `app/api/routes/evaluation.py` (`POST /evaluation/run`).

## Known Gotchas

Dataset é sintético (6 casos: match forte, match fraco, match parcial, duas bordas, sem
experiência) — cobre direção geral, não é golden dataset validado por um recrutador humano de
verdade. Rodar o harness custa ~24 chamadas de LLM por execução; a rota HTTP roda tudo síncrono
(sem Celery) — uma chamada a `/evaluation/run` bloqueia a requisição por dezenas de segundos.
Endpoint interno de dev, sem controle de custo/acesso — não expor publicamente sem pensar em
autenticação/rate limit (mesmo ponto já levantado pro resto da API).
