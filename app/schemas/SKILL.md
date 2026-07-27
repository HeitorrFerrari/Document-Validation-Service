---
name: schemas
description: Business rules, internal patterns, and communication contracts for the schemas
  module. Load before working on any feature in app/schemas.
---

# Module: schemas

**Path:** `app/schemas/`

## Responsibility

Modelos Pydantic — o contrato de forma pra toda saída estruturada de LLM e todo documento Mongo.

## Business Rules

Todo campo validado por Pydantic v2 antes de qualquer persistência ou resposta HTTP — o LLM nunca
decide a forma, só o conteúdo (reforçado em cada `agent.py` que os usa).

## Internal Patterns

**Structure:**
```
app/schemas/
├── extracted_resume.py    # CurriculoExtraido, Experience
├── job_requirements.py     # JobRequirements
├── validation_result.py    # ValidationResult, RequirementScore
├── judge_result.py          # JudgeResult (crítica independente do validator, ver app/judge)
└── chat.py                 # ChatMessage, ChatRequest, ChatResponse
```

**Naming:** um arquivo por entidade principal, nomes em inglês (exceção histórica:
`CurriculoExtraido`, resto em inglês).

## Relationships

### Emits / Consumes
Nada — módulo puramente declarativo.

### Depends On
Nada de interno. Dependido por quase todo o resto do projeto.

## Known Gotchas

Sem versionamento de schema — se um campo for adicionado/removido, documentos Mongo já persistidos
com o shape antigo vão falhar validação Pydantic na leitura (`get_resume`/`get_validation_result`),
porque não há `model_config = ConfigDict(extra=...)` relaxado nem passo de migração. Mudança de
schema precisa considerar dados já gravados, não só o código.
