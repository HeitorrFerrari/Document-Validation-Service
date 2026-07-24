# Validador de Currículo — contexto do projeto

Pipeline de IA que recebe currículo (PDF/DOCX) + requisitos de vaga, extrai dados, valida
elegibilidade e gera feedback. Projeto de aprendizado, construído por fases (ver
`requirements.txt`, Fase 0 a Fase 10). Usuário está praticando padrões complexos de propósito —
não sugerir simplificação/redução de escopo sem que ele peça.

**`README.md` está desatualizado** — ainda diz que RAG/chat "não implementados". Não confiar nele
pra status; usar este arquivo + `git log` como fonte da verdade.

## Status real por fase (verificado no código, não só no README)

| Fase | O quê | Status |
|---|---|---|
| 0 | Chamada única OpenAI, schemas Pydantic | ✅ |
| 1/2 | Estado conversacional + agente com tools | ✅ (`app/graph/graph.py`, `app/states/state.py`) |
| 3 | Guardrails | ⚠️ parcial — só formato de arquivo + texto extraído (`app/guard/guard.py`). Nada de guardrail pro chat ainda |
| 4 | RAG (Qdrant) | ✅ implementado, ❌ **não conectado** ao fluxo principal |
| 5 | Orquestração LangGraph multi-nó | ✅ (`app_graph`: extract → validation → feedback) |
| 6 | Persistência Mongo | ✅ testado ponta a ponta |
| 7 | Fila Celery/Redis | ✅ testado ponta a ponta |
| 8 | API FastAPI | ✅ `/cv/analyze` + `/cv/status/{task_id}` |
| 9 | Chat conversacional (RAG sobre o resultado) | ⚠️ grafo pronto (`app/chats/`), ❌ **sem rota, sem ingestão chamada, sem checkpointer** |
| 10 | Observabilidade / avaliação contínua | ❌ stub (`app/evaluation/evaluation.py`) |

## Dois grafos LangGraph — não confundir

- **`app/graph/graph.py`** (`app_graph`) — pipeline de validação: extract → validation → feedback.
  Chamado dentro de `app/worker/tasks.py::analisar_curriculo_task` (via Celery, não via `.invoke`
  direto no grafo — os nós são chamados como funções soltas na task, o grafo em si não é invocado
  no fluxo real ainda; conferir se isso é intencional antes de assumir que `app_graph.invoke` é o
  caminho usado em produção).
- **`app/chats/chat_graph.py`** (`chat_graph`) — chat pós-análise: retrieve (Qdrant) → generate
  (gpt-4o-mini). Existe e compila, mas **nenhum lugar do código o invoca** — sem rota em
  `app/api/routes/`, sem wiring em `app/main.py`.

## Fluxo real ponta a ponta hoje

`POST /cv/analyze` (multipart: `file` + `job` JSON) → salva job no Mongo → dispara
`analisar_curriculo_task.delay()` (Celery) → task valida formato/texto (guard) → extrai currículo
→ salva resume → valida elegibilidade → salva validation → gera feedback → resultado consultável
em `GET /cv/status/{task_id}`.

**RAG e chat rodam fora desse fluxo** — `ingest_session()` (`app/rag/ingest.py`) nunca é chamada
pela task ou pela rota. Sem ingestão, `chat_graph` não teria contexto pra recuperar mesmo se
tivesse rota.

## Pendências conhecidas (próximos passos prováveis)

1. Chamar `ingest_session()` no fim de `analisar_curriculo_task` (ou em rota separada) pra
   popular o Qdrant.
2. Decidir a fonte de `session_id` usado em `chat_state.py`/`ingest.py`/`retriever.py` — hoje não
   existe conceito de sessão no Mongo (`job_id`/`resume_id`/`validation_id` são os IDs que
   existem). Precisa decidir antes de wirar o endpoint.
3. Criar rota (`app/api/routes/`) que chama `chat_graph.invoke(...)`.
4. Adicionar checkpointer no `chat_graph` pra memória entre turnos (hoje é stateless por invoke,
   exceto o que for passado manualmente em `messages`).
5. Guardrails pro chat (Fase 3 hoje só cobre a extração inicial).
6. `app/core/config.py` define `settings.qdrant_collection = "curriculos"` mas
   `app/rag/qdrant_client.py` **ignora isso e hardcoda** `COLLECTION_NAME = "cv_chat_session"` —
   inconsistência a resolver quando mexer no RAG.
7. Fase 10 (observabilidade/avaliação contínua) ainda não começada.

## Gotchas operacionais

- Celery worker **não recarrega código sozinho** — depois de mexer em `app/worker/tasks.py` ou
  qualquer módulo importado por ele (extractors, agentes, schemas), precisa `Ctrl+C` e subir de
  novo (`celery -A app.worker.tasks worker --loglevel=info`).
- `docker` sem `sudo` pode dar permission denied se o usuário não estiver no grupo `docker`.
- Mongo e Redis rodam em containers Docker locais (`validador-mongo`, porta 27017;
  `validador-redis`, porta 6379). Qdrant local em `http://localhost:6333` (não documentado no
  README — falta instrução de como subir).
- Testes em `app/tests/db_tests` e `app/tests/api_tests` esperam Mongo/API rodando de verdade, não
  são unit tests isolados.

## Mapa de diretórios

- `app/agents/` — validator (scoring) + feedback (agentes com LLM)
- `app/api/` — extração + rotas FastAPI
- `app/chats/` — grafo de chat (Fase 9, não wirado)
- `app/core/` — config (env vars) + logging
- `app/db/` — conexão Mongo + repositórios (job/resume/validation)
- `app/evaluation/` — stub Fase 10
- `app/extractions/` — extração de texto de PDF/DOCX
- `app/graph/` — grafo principal de validação (Fase 5)
- `app/guard/` — guardrails de formato/texto (Fase 3, parcial)
- `app/judge/` — stub (não explorado ainda)
- `app/rag/` — Qdrant client + ingest + retriever (Fase 4, não conectado ao fluxo)
- `app/schemas/` — Pydantic (CurriculoExtraido, JobRequirements, ValidationResult)
- `app/states/` — TypedDict do `app_graph`
- `app/tools/` — tools do agente (ex.: pedir mais info no currículo)
- `app/worker/` — task Celery que roda o pipeline
- `app/tests/` — unit + api_tests + db_tests + graph_tests
