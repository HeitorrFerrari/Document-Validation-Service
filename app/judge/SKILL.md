---
name: judge
description: Business rules, internal patterns, and communication contracts for the judge
  module. Load before working on any feature in app/judge.
---

# Module: judge

**Path:** `app/judge/`

## Responsibility

LLM-as-judge: audita a consistência do `ValidationResult` + feedback já produzidos pelo
validator/feedback (`app/agents`) contra o currículo e a vaga originais. Não reavalia elegibilidade
do zero — é uma segunda opinião sobre a qualidade do que já foi decidido.

## Business Rules

- Roda síncrono, dentro de `analisar_curriculo_task`, logo após persistir o `ValidationResult`.
- Falha do judge (timeout, erro de API, schema inválido) nunca derruba o pipeline — isolada em
  `try/except` no worker, só loga via `trace("judge", "error", ...)`.
- `JudgeResult.validation_id` é setado pelo worker (não pelo `judge.py`), mesmo padrão de
  `resultado.resume_id`/`resultado.job_id` em `app/agents/validator`.

## Internal Patterns

**Structure:**
```
app/judge/
└── judge.py   # evaluate(resume, job, validation, feedback) -> JudgeResult
```

**Key abstractions:** mesmo padrão de `client.chat.completions.parse(...,
response_format=JudgeResult)` usado no validator; usa `app/prompts/base.build_system_prompt`.

## Relationships

### Emits
Nada diretamente — retorna `JudgeResult`, quem persiste é o chamador.

### Consumes
Nada de outro módulo em runtime além dos schemas de entrada.

### Depends On
`app/schemas` (`JudgeResult`, `ValidationResult`, `CurriculoExtraido`, `JobRequirements`),
`app/prompts/base`, `app/core/config`.

Chamado por `app/worker/tasks.py`, resultado persistido via
`app/db/repositories/judge_repository.py`.

## Known Gotchas

`app/evaluation/` (o outro stub Fase 10) continua vazio — precisaria de um dataset de referência
que não existe, ficou fora deste lote (ver `app/evaluation/SKILL.md`). `judge` roda síncrono por
decisão explícita (simplicidade > latência zero para o usuário, que já espera via polling
assíncrono do Celery).
