---
name: db
description: Business rules, internal patterns, and communication contracts for the db
  module. Load before working on any feature in app/db.
---

# Module: db

**Path:** `app/db/`

## Responsibility

Conexão MongoDB + funções de repositório flat pras três entidades persistidas (vaga, currículo,
validação).

## Business Rules

`_id` (ObjectId do Mongo) nunca escapa desse módulo — todo o resto do código trata id como string
(`str(ObjectId)` na escrita, `ObjectId(str)` na leitura).

## Internal Patterns

**Structure:**
```
app/db/
├── mongo.py                        # MongoClient + handle `db`, construído a partir de settings
└── repositories/
    ├── job_repository.py           # save_job / get_job -> coleção "jobs"
    ├── resume_repository.py        # save_resume / get_resume -> coleção "resumes"
    ├── validation_repository.py    # save_validation_result / get_validation_result -> "validations"
    └── judge_repository.py         # save_judgement / get_judgement -> "judgements" (busca por validation_id, não por _id)
```

**Naming:** par `save_x`/`get_x` por coleção, sem classe/ORM. `documento.pop("_id")` antes de
reidratar no schema Pydantic.

**Key abstractions:** id como string é o tipo em toda fronteira acima deste módulo — só aqui dentro
existe `ObjectId`.

## Relationships

### Emits
Nada.

### Consumes
Nada de outro módulo.

### Depends On
`app/schemas`, `app/core/config` (via `mongo.py`).

Consumido por: `app/api/routes/cv.py` (save_job), `app/worker/tasks.py` (save_resume,
save_validation_result).

## Known Gotchas

`get_job`/`get_resume` existem mas **nunca são chamados** em lugar nenhum do fluxo real hoje —
caminho é write-only (nenhuma rota lê vaga/currículo de volta por id; só o resultado da validação
flui adiante, via resultado do Celery e via RAG). Não existe `session_repository` — o conceito de
sessão (RAG/chat) usa `validation_id` emprestado, sem coleção/repositório próprio.
