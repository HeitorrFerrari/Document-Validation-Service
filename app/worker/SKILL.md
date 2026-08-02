---
name: worker
description: Business rules, internal patterns, and communication contracts for the worker
  module. Load before working on any feature in app/worker.
---

# Module: worker

**Path:** `app/worker/`

## Responsibility

App Celery + a única task de background que roda o pipeline completo de análise (guard → extrai
texto → `app_graph.invoke` [extrai currículo → valida → feedback] → persiste resume → persiste
validação → judge (crítica independente, best-effort) → ingestão RAG).

## Business Rules

- Arquivo temporário enviado é sempre removido em bloco `finally`, mesmo se guard/extração falhar.
- `session_id` usado no RAG é sempre `validation_id`.

## Internal Patterns

**Structure:**
```
app/worker/
├── tasks.py   # celery_app, analisar_curriculo_task
└── cache.py    # stub, não implementado
```

## Relationships

### Emits
Nada além do resultado da task (consumido via Celery backend/`AsyncResult`, sem evento explícito).

### Consumes
Nada de fila — só é disparado.

### Depends On
`app/guard`, `app/extractions`, `app/graph` (`app_graph.invoke`, que por sua vez orquestra
`app/agents` e `app/api/extraction`), `app/judge`, `app/db/repositories`, `app/rag/ingest`,
`app/core/config`.

Disparado por `app/api/routes/cv.py` via `.delay(...)`.

## Known Gotchas

**Worker não recarrega código sozinho.** Qualquer edição em `tasks.py` ou em qualquer módulo que ele
importa (extractors, agents, schemas, rag) exige reiniciar manualmente
(`celery -A app.worker.tasks worker --loglevel=info`) — causa clássica de "corrigi o bug mas o erro
continua" nesse projeto. `cache.py` é stub vazio — nenhum cache Redis está implementado, apesar do
rótulo "Fase 7" cobrir isso no `CLAUDE.md` (Fase 7 cobre a fila Celery, que funciona; o cache é a
parte não feita).
