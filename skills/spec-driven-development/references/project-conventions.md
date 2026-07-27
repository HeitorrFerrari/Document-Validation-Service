# Project Conventions — Validador de Currículo

## Stack

Python 3.14, FastAPI + uvicorn, Celery + Redis, MongoDB (pymongo), Qdrant (`qdrant-client`),
OpenAI SDK direto (`chat.completions.parse/create`) + LangChain/LangGraph só em `app/chats` e
`app/graph`, Pydantic v2, pypdf, python-docx. Frontend estático (HTML/CSS/JS vanilla, sem build
step) servido same-origin via `StaticFiles`.

## Module structure (flat, one concern per top-level `app/*` dir)

```
app/
├── agents/{validator,feedback}/agent.py   # uma função por chamada LLM
├── api/{routes/*, extraction/}
├── chats/                                  # LangGraph do chat pós-análise
├── core/                                   # config, logging, tracing (leaf, sem deps internas)
├── db/{mongo.py, repositories/*}
├── evaluation/, judge/                     # stubs Fase 10
├── extractions/{pdf,docx}/
├── graph/                                  # app_graph (não usado no fluxo real, ver gotcha)
├── guard/
├── rag/{qdrant_client,ingest,retriever}.py
├── schemas/                                 # Pydantic, fonte da verdade de forma
├── states/                                  # TypedDict do app_graph
├── tools/                                   # quebrado/morto hoje
├── worker/tasks.py                          # Celery, orquestra o pipeline de verdade
└── static/                                  # frontend
```

## File/naming conventions

- Função de chamada LLM: `agent.py` dentro de um submódulo nomeado pelo papel (`validator/`,
  `feedback/`).
- Repositório Mongo: `<entidade>_repository.py` com `save_x(obj) -> str` / `get_x(id) -> Model | None`
  soltos, sem classe. `_id` (ObjectId) nunca escapa do módulo — vira string em todo o resto do código.
- Schema Pydantic: um arquivo por entidade em `app/schemas/`, nomes em inglês (`CurriculoExtraido` é
  a exceção histórica — resto segue em inglês: `JobRequirements`, `ValidationResult`).
- Toda saída estruturada de LLM passa por `response_format=PydanticModel` — nunca parsing manual de
  string.
- Env vars só deveriam ser lidas via `app/core/config.py::settings` (nem sempre respeitado hoje —
  ver `app/rag/SKILL.md` gotcha do Qdrant hardcoded; ao tocar em módulo com env var solta, migrar
  pra `settings` como parte da tarefa).
- Docstrings/comentários em português, identificadores de biblioteca em inglês.

## Test pattern

- `app/tests/db_tests/`, `app/tests/api_tests/` — scripts manuais (`test_manual_*.py`), exigem
  Mongo/Redis/Qdrant/API rodando de verdade, sem assert real. **Não conte com eles como gate CI.**
- `app/tests/graph_tests/test_graph.py` — único teste que exercita `app_graph` (que não é usado em
  produção).
- Não existe teste automatizado real hoje para `app/agents`, `app/chats`, `app/rag`, `app/guard`,
  `app/core/tracing`, `app/api/routes/chat.py`. Ao aplicar TDD imutável (fase 1) neste projeto, usar
  `pytest` puro com mocks do cliente OpenAI/Qdrant/Mongo (não bater em serviço real) — os testes
  novos devem poder rodar sem Docker/serviços de pé, diferente dos `test_manual_*` existentes.

## Representative module tree (app/rag — exemplo de módulo "cheio")

```
app/rag/
├── qdrant_client.py   # get_qdrant_client(), COLLECTION_NAME, VECTOR_SIZE
├── ingest.py           # _build_chunks (privado), ingest_session, delete_session
└── retriever.py        # retrieve(session_id, query, top_k)
```
