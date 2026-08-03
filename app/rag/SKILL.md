---
name: rag
description: Business rules, internal patterns, and communication contracts for the rag
  module. Load before working on any feature in app/rag.
---

# Module: rag

**Path:** `app/rag/`

## Responsibility

Cliente Qdrant, ingestão (chunk + embed + upsert) de uma sessão de validação, e retrieval
(embed da pergunta + similarity search) pro chat.

## Business Rules

- Point ID sempre `uuid5(NAMESPACE_URL, f"{session_id}-{i}")` — determinístico, então reingerir a
  mesma sessão faz upsert, não duplica.
- Retrieval sempre filtra por `session_id` no payload — sessões nunca se misturam na busca.

## Internal Patterns

**Structure:**
```
app/rag/
├── qdrant_client.py  # get_qdrant_client(), COLLECTION_NAME, VECTOR_SIZE (hardcoded, ver gotcha)
├── ingest.py         # _build_chunks (privado), ingest_session(session_id, resume, job, validation), delete_session
└── retriever.py       # retrieve(session_id, query, top_k=4) -> list[str]
```

**Key abstractions:** chunk é uma string legível por humano por experiência/formação/skills/
critério de score/nota final — não é chunking genérico por janela de caracteres/tokens.

## Relationships

### Emits
Chamadas `trace()` (`app/core/tracing`).

### Consumes
Nada de outro módulo do projeto (só OpenAI embeddings + Qdrant client).

### Depends On
`app/core/config` (nominalmente — ver gotcha), `app/schemas`.

Consumido por `app/worker/tasks.py` (`ingest_session`) e `app/chats/chat_graph.py` (`retrieve`, via
`retriever`).

## Known Gotchas

`COLLECTION_NAME`/URL agora vêm de `settings.qdrant_collection`/`settings.qdrant_url` (antes eram
hardcoded `"cv_chat_session"`/`"http://localhost:6333"`). Sessões ingeridas antes dessa mudança
ficaram na collection antiga — não migram automaticamente, ver `DECISIONS.md`. `delete_session`
existe mas nunca é chamado de lugar nenhum — sem limpeza/TTL de sessão, o Qdrant cresce
indefinidamente.

teste
