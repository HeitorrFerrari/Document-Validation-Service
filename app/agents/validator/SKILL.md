---
name: validator-agent
description: Agente que avalia elegibilidade de um candidato para uma vaga, comparando currículo estruturado com requisitos e retornando score + justificativa
---

# Validator Agent

Localização: `app/agents/validator/agent.py` (função `validate_eligibility`) + `app/agents/validator/scoring.py` (helper `calcular_anos_experiencia`).

## O que faz

Recebe um `CurriculoExtraido` (já extraído/estruturado pela Fase 0) e um `JobRequirements`,
e retorna um `ValidationResult` validado via `response_format=ValidationResult`
(structured output da OpenAI — o LLM não decide o formato, só o conteúdo).

Avalia CADA requisito da vaga separadamente (skills obrigatórias, skills desejáveis, anos de
experiência, formação mínima), cada um com nota 0–100 e um detalhe curto justificando. O score
geral é a média ponderada dessas notas.

## Regras de negócio importantes

- **Anos de experiência não é estimado pelo LLM.** `calcular_anos_experiencia()` (scoring.py)
  calcula isso determinística/programaticamente a partir de `resume.experience` (soma meses entre
  `data_inicio`/`data_fim` de cada experiência, tratando `"atual"/"presente"/"current"/"present"`
  como data-fim = hoje). Esse valor pronto é injetado no prompt — o LLM só usa o número, não
  estima a partir das datas brutas.
- O prompt instrui o modelo a usar **apenas** skills/experiências presentes no currículo — nunca
  assumir competência não listada.
- `job.description` (se presente) é contexto qualitativo (senioridade, escopo), não um critério
  pontuado à parte.
- Modelo e temperatura vêm de `settings.openai_main_model` / `settings.openai_temperature`
  (`app/core/config.py`).

## Onde é chamado

Node de validação do `app_graph` (`app/graph/graph.py`), executado dentro de
`analisar_curriculo_task` (`app/worker/tasks.py`), via Celery.

## Observabilidade

Cada chamada gera um `trace("llm", "validate", model=..., total_tokens=...)`
(`app/core/tracing.py`) para rastrear uso de tokens.

## Gotchas

- `_parse_periodo` em `scoring.py` espera datas no formato `"YYYY"` ou `"YYYY-MM"` — não trata
  outros formatos.
- Se `data_inicio` estiver ausente/mal formatada, `_parse_periodo` lança exceção (sem tratamento
  de erro hoje).
- Alterar este arquivo exige reiniciar o worker Celery (não recarrega sozinho — ver CLAUDE.md).
