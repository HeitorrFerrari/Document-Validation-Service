---
name: chats
description: Business rules, internal patterns, and communication contracts for the chats
  module. Load before working on any feature in app/chats.
---

# Module: chats

**Path:** `app/chats/`

## Responsibility

Fluxo LangGraph de chat (retrieve no Qdrant → generate via LLM) pra debater o resultado de uma
sessão de validação já processada.

## Business Rules

- `load_session_node` busca o `ValidationResult` completo no Mongo (não no Qdrant) antes de
  qualquer coisa — a nota geral, elegibilidade e reasoning vão SEMPRE no system prompt, de forma
  determinística. RAG (Qdrant) só complementa com detalhe por critério.
- Sessão sem `ValidationResult` no Mongo levanta `ValueError`, traduzido pra HTTP 404 na rota (não
  deixa o LLM alucinar contexto pra sessão inexistente).
- Sem checkpointer: o histórico completo (`messages`) vai e volta no corpo da requisição — o
  cliente (frontend) é responsável por reenviar o que recebeu na resposta anterior.
- `generate_node` faz bind de tools conversacionais (`app/chats/tools.py`) no LLM. Cada tool
  cobre uma pergunta provável (nota geral, elegibilidade, pontos fortes/fracos, orientação,
  critério específico) e devolve um texto PRONTO, não gerado pelo LLM — o prompt instrui o modelo
  a só encaixar o texto da tool, não reescrever. É assim que a resposta fica consistente entre
  sessões em vez de variar "tom de IA" a cada pergunta parecida. Loop de tool-calling limitado a
  uma rodada (não é ReAct de propósito aberto).

## Internal Patterns

**Structure:**
```
app/chats/
├── chat_state.py   # ChatState TypedDict: session_id, question, messages, retrieved_context, validation
├── tools.py          # build_conversational_tools(validation) -> tools com texto pré-escrito por categoria
└── chat_graph.py    # load_session_node -> retrieve_node -> generate_node (com tools), compilado como chat_graph
```

**Key abstractions:** único lugar do código que usa `ChatOpenAI` (wrapper LangChain) em vez do SDK
puro da OpenAI — necessário pra `.invoke([...messages])` com tipos de mensagem LangChain, encaixando
no estado do LangGraph.

## Relationships

### Emits
Chamadas `trace()` (`app/core/tracing`); chama `app.rag.retriever.retrieve`.

### Consumes
Invocado por `app/api/routes/chat.py`.

### Depends On
`app/rag/retriever`, `app/db/repositories/validation_repository`, `app/prompts/base`,
`app/core/tracing`, `app/core/config` (indiretamente, via env var do `ChatOpenAI`).

## Known Gotchas

Sem checkpointer LangGraph (`MemorySaver` ou equivalente não wireado) — "memória" é inteiramente
gerenciada pelo cliente. Sem guardrail nenhum sobre `question` — é o ponto mais exposto a prompt
injection/conteúdo fora de escopo do projeto inteiro, já que recebe input livre do usuário via chat
aberto (nem o guardrail básico de `app/guard` se aplica aqui, ele só cobre o upload inicial;
`app/prompts/base` cobre o system prompt, não filtra o input do usuário).
