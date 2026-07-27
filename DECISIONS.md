# Decisões de arquitetura

Log de decisões não óbvias a partir do código, com data e motivo curto. Não é changelog de
feature — é o "por quê" por trás de escolhas que alguém lendo só o código não recuperaria.

## 2026-07-27 — Remover `app/tools/tools.py` e `GraphState.need_more_infos`

`tools.py` nunca importou com sucesso (`from json import tool` e `from langchain_core.tools import
Tools` — ambos errados) e nunca foi referenciado em lugar nenhum do código (confirmado via grep).
`need_more_infos` era campo morto no mesmo espírito — nunca setado, nunca lido. Os dois eram, juntos,
a base abandonada de um fluxo de "pedir mais informação ao candidato" via tool-calling no validator.
Decisão: remover em vez de consertar — o validator continua respondendo sempre com o que tem no
currículo. Se o fluxo de "pedir mais info" for retomado no futuro, é implementação nova, não
reaproveitamento deste código.

## 2026-07-27 — `app_graph` passa a ser o caminho real de execução

`app/graph/graph.py` (LangGraph, Fase 5) nunca era invocado — `app/worker/tasks.py` chamava
`extrair_curriculo`, `validate_eligibility`, `build_feedback` como funções soltas, duplicando o
caminho que o grafo já representava. Decisão: migrar `analisar_curriculo_task` pra chamar
`app_graph.invoke(...)` de verdade, eliminando o caminho duplicado, em vez de apagar o grafo.
`resume_id`/`job_id` do `ValidationResult` continuam setados na task, depois do `.invoke()`, porque
só existem depois da persistência no Mongo (o grafo não tem esses valores no seu estado).

## 2026-07-27 — `judge.py` roda síncrono, dentro da task Celery

O evaluator LLM-as-judge (Fase 10) audita a consistência do `ValidationResult`+feedback já gerados.
Decisão: rodar como mais um passo dentro de `analisar_curriculo_task`, não como job offline/batch
separado. Motivo: simplicidade de implementação agora — o custo é mais uma chamada LLM de latência
no worker, mas isso não afeta o usuário (que já espera o resultado via polling assíncrono do
Celery). Falha do judge é isolada em `try/except` próprio e nunca derruba o pipeline principal —
é observabilidade, não faz parte do contrato de resposta ao candidato.

## 2026-07-27 — Qdrant collection migrou de `cv_chat_session` (hardcoded) pra `settings.qdrant_collection`

`app/rag/qdrant_client.py` ignorava `settings.qdrant_url`/`settings.qdrant_collection` e hardcodava
`"cv_chat_session"`/`"http://localhost:6333"`. Corrigido pra usar `settings`. Efeito colateral aceito:
sessões de chat ingeridas antes dessa mudança ficam na collection antiga (`cv_chat_session`) e
perdem acesso ao contexto RAG específico por critério — o chat continua funcionando pra elas porque
a nota/elegibilidade agora vem direto do Mongo (`load_session_node`), só os chunks de detalhe somem.
Sem lógica de migração de dados escrita — ambiente de desenvolvimento/aprendizado, não produção com
usuários reais.
