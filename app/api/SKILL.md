---
name: api
description: Business rules, internal patterns, and communication contracts for the api
  module. Load before working on any feature in app/api.
---

# Module: api

**Path:** `app/api/`

## Responsibility

Superfície HTTP (routers FastAPI) + a chamada LLM que transforma texto bruto do currículo em
`CurriculoExtraido`.

## Business Rules

- Prompt de extração: nunca inventar dado que não esteja literalmente no texto.
- `/cv/status/{task_id}` deve SEMPRE retornar 200 com `{status, detail}` em falha — nunca levantar
  `HTTPException`. Isso é contrato documentado (README) e é consumido pelo frontend (polling).

## Internal Patterns

**Structure:**
```
app/api/
├── routes/
│   ├── cv.py                    # POST /cv/analyze, GET /cv/status/{task_id}
│   ├── chat.py                   # POST /chat/{session_id}
│   ├── evaluation.py             # POST /evaluation/run — dispara app/evaluation contra o dataset
│   └── input/
│       └── requirements.py       # POST /requirements/ — hoje só ecoa o JobRequirements recebido
└── extraction/
    └── extract_data.py           # extrair_curriculo(text) -> CurriculoExtraido
```

**Naming:** router por recurso (`cv`, `chat`, `requirements`), `prefix=` no `APIRouter` casa com o
nome do arquivo.

**Key abstractions:** `extrair_curriculo` usa o mesmo padrão `client.chat.completions.parse(...,
response_format=Schema)` do validator (ver `app/agents/SKILL.md`).

## Relationships

### Emits
`analisar_curriculo_task.delay(...)` (dispara pro Celery, ver `app/worker/SKILL.md`);
`chat_graph.invoke(...)` (síncrono, dentro do próprio processo uvicorn, ver `app/chats/SKILL.md`).

### Consumes
`AsyncResult` do Celery pra montar a resposta de `/cv/status`.

### Depends On
`app/db/repositories` (save_job), `app/worker/tasks`, `app/chats/chat_graph`, `app/schemas`.

## Known Gotchas

`app/api/routes/input/requirements.py` é um no-op — recebe `JobRequirements` já pronto e devolve
igual, não extrai requisitos de um texto de vaga (ao contrário do currículo, que tem extração real
via LLM). Se a intenção for simetria (texto da vaga → `JobRequirements` estruturado via LLM), essa
rota precisa ser reescrita, não é isso hoje.

Nenhuma pendente — docstring de `POST /cv/analyze` corrigida pra refletir persistência + fluxo
assíncrono via Celery.
