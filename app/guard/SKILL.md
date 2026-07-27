---
name: guard
description: Business rules, internal patterns, and communication contracts for the guard
  module. Load before working on any feature in app/guard.
---

# Module: guard

**Path:** `app/guard/`

## Responsibility

Guardrails pré-LLM: sniff de formato de arquivo por magic bytes, checagem de tamanho mínimo do
texto extraído.

## Business Rules

- PDF/DOCX detectados pela assinatura de bytes (`%PDF-`, `PK\x03\x04` + `word/document.xml` dentro
  do zip), nunca pela extensão do nome do arquivo.
- Texto extraído com menos de 50 caracteres aborta o pipeline (`ValueError`) — evita mandar
  string vazia/curta pro LLM e receber alucinação de volta.

## Internal Patterns

**Structure:**
```
app/guard/
└── guard.py   # check_document_format(path) -> "pdf"|"docx", check_extracted_text(text, min_length=50)
```

## Relationships

### Emits
Nada (levanta `ValueError` em caso de falha).

### Consumes
Nada.

### Depends On
Nada de interno.

Consumido só por `app/worker/tasks.py`, no início de `analisar_curriculo_task`.

## Known Gotchas

Apesar do rótulo "Fase 3 — Guardrails" no `CLAUDE.md` sugerir escopo amplo, este módulo cobre só
formato de arquivo + presença de texto. **Não existe guardrail de prompt injection, PII, ou
conteúdo fora de escopo em lugar nenhum do projeto** — nem aqui nem no chat (ver
`app/chats/SKILL.md`, que é o ponto mais exposto hoje).
