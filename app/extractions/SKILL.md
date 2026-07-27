---
name: extractions
description: Business rules, internal patterns, and communication contracts for the extractions
  module. Load before working on any feature in app/extractions.
---

# Module: extractions

**Path:** `app/extractions/`

## Responsibility

Extração de texto bruto a partir do arquivo enviado, um extrator por formato suportado.

## Business Rules

Ambos assumem que o arquivo tem camada de texto (sem OCR) — texto insuficiente é pego depois por
`app/guard::check_extracted_text`, não aqui.

## Internal Patterns

**Structure:**
```
app/extractions/
├── pdf/pdf_extractor.py    # extrair_texto_pdf(path) -> str, via pypdf
└── docx/docx_extractor.py  # extrair_texto_docx(path) -> str, via python-docx
```

**Key abstractions:** ambos retornam texto puro concatenado (páginas/parágrafos com `\n`), sem
preservar estrutura (tabelas, colunas, formatação).

## Relationships

### Emits
Nada.

### Consumes
Nada.

### Depends On
Nada de interno — só as libs `pypdf`/`python-docx`.

Consumido só por `app/worker/tasks.py`, escolhido pelo tipo detectado em
`app/guard::check_document_format`.

## Known Gotchas

Sem tratamento de erro além do que `pypdf`/`python-docx` levantam nativamente. PDF escaneado (sem
camada de texto) retorna string vazia/quase vazia silenciosamente — só é pego depois, pelo check de
tamanho mínimo em `app/guard`. Não há fallback de OCR.
