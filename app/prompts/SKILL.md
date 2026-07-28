---
name: prompts
description: Business rules, internal patterns, and communication contracts for the prompts
  module. Load before working on any feature in app/prompts.
---

# Module: prompts

**Path:** `app/prompts/`

## Responsibility

Fragmentos de system prompt compartilhados por todo agente que chama LLM: tom/idioma, persona de
RH, defesa de prompt injection, e o guard de escopo (só responde sobre a avaliação do currículo).
Existe pra padronizar o que cada `agent.py` escreve, em vez de cada um reinventar o próprio texto.

## Business Rules

- `INJECTION_GUARD` é incluído por padrão (`include_injection_guard=True`) — todo agente que
  processa dado externo (currículo, vaga, mensagem do usuário) deve mantê-lo.
- `SCOPE_GUARD` é opt-in (`include_scope_guard=False` por padrão) — só faz sentido em contexto
  conversacional livre (o chat). Extração/validator/feedback são single-shot, não precisam.
- `RH_PERSONA` é usado pelos dois pontos que falam diretamente com o candidato (`app/chats`,
  `app/agents/feedback`) — linguagem formal, sem jargão técnico, sem prometer revisão de nota, e
  com regras de estilo explícitas (frases banidas, sem exclamação, resposta direta sem preâmbulo)
  pra reduzir "cara de IA genérica" nas respostas.

## Internal Patterns

**Structure:**
```
app/prompts/
└── base.py   # RESPONSE_CONTRACT, RH_PERSONA, INJECTION_GUARD, SCOPE_GUARD, build_system_prompt()
```

**Naming:** cada fragmento é uma constante `UPPER_SNAKE_CASE`; `build_system_prompt(role_instructions,
*, include_injection_guard=True, include_scope_guard=False)` compõe o prompt final.

**Key abstractions:** módulo é só texto + uma função de composição — sem estado, sem I/O.

## Relationships

### Emits / Consumes
Nada.

### Depends On
Nada (módulo folha).

Consumido por `app/api/extraction/extract_data.py`, `app/agents/validator/agent.py`,
`app/agents/feedback/agent.py`, `app/judge/judge.py`, `app/chats/chat_graph.py`.

## Known Gotchas

`SCOPE_GUARD` é mitigação em nível de prompt, não um classificador/filtro de código — um modelo
pode ainda ser convencido a fugir do escopo com adversarial prompting insistente. Não é bloqueio
garantido, é redução de superfície.
