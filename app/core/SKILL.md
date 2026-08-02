---
name: core
description: Business rules, internal patterns, and communication contracts for the core
  module. Load before working on any feature in app/core.
---

# Module: core

**Path:** `app/core/`

## Responsibility

Infra transversal: settings orientado a env var, setup de logging, trace visual de terminal.

## Business Rules

Nenhuma regra de negócio — módulo de infraestrutura pura.

## Internal Patterns

**Structure:**
```
app/core/
├── config.py    # classe Settings, lê todo env var via os.getenv, instância única `settings`
├── logging.py    # get_logger(name) -> logger stdlib com basicConfig(INFO)
└── tracing.py     # trace(tag, step, **fields) -> linha colorida (ANSI) via logging
```

**Naming:** `settings` é o único símbolo exportado de `config.py`, importado como
`from app.core.config import settings` em todo o resto do projeto.

**Key abstractions:** `settings` é pensado como singleton "substitui os.getenv espalhado" (docstring
do próprio arquivo) — mas esse contrato não é respeitado por todo mundo, ver gotcha.

## Relationships

### Emits
Nada.

### Consumes
Nada — módulo folha, sem dependência interna.

### Depends On
Nenhuma (folha da árvore de imports). Consumido por quase todo o resto: inicialização de clientes
(Mongo, OpenAI), URIs de banco, chamadas `trace()` em `app/rag` e `app/chats`.

## Known Gotchas

Nenhuma pendente. `settings.qdrant_url`/`settings.qdrant_collection` agora são de fato consumidos
por `app/rag/qdrant_client.py` — antes eram lidos de env var e ignorados (hardcode local),
quebrando o contrato de "um lugar só lê env var" que este módulo promete.
