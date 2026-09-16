---
name: feedback-agent
description: Agente que redige o texto de feedback em linguagem natural explicando ao candidato o resultado da avaliação do currículo
---

# Feedback Agent

Localização: `app/agents/feedback/agent.py` (função `build_feedback`).

## O que faz

Recebe um `ValidationResult` (já calculado pelo validator agent) e gera um texto em linguagem
natural (não estruturado — `chat.completions.create`, sem `response_format`) explicando ao
candidato o resultado da avaliação, de forma clara e construtiva.

**Não reavalia o currículo.** Só comunica a decisão que o validator já tomou — usa a persona
`RH_PERSONA` (`app/prompts/base.py`) e é instruído a usar **apenas** as notas/detalhes do
`ValidationResult` recebido, nunca inventar, alterar ou presumir informação que não esteja ali.

## Onde é chamado

Node de feedback do `app_graph` (`app/graph/graph.py`), executado depois do node de validação,
dentro de `analisar_curriculo_task` (`app/worker/tasks.py`), via Celery.

O resultado (texto) é persistido — ver pendência de feedback persistence (Fase 6, já implementada
segundo histórico do projeto: schema + repositório de feedback, integrado à task e exposto no
endpoint de sessão).

## Observabilidade

Cada chamada gera um `trace("llm", "feedback", model=..., total_tokens=...)`
(`app/core/tracing.py`) para rastrear uso de tokens.

## Gotchas

- Modelo e temperatura vêm de `settings.openai_main_model` / `settings.openai_temperature`
  (`app/core/config.py`) — mesmo modelo do validator, sem override específico para feedback.
- Sem `response_format`/schema Pydantic aqui — saída é texto livre, diferente do validator que é
  structured output. Não confundir os dois padrões ao mexer em qualquer um dos agentes.
- Alterar este arquivo exige reiniciar o worker Celery (não recarrega sozinho — ver CLAUDE.md).
