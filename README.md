# Validador de Currículo

Pipeline de IA que recebe um currículo (PDF/DOCX) + os requisitos de uma vaga, extrai os dados do currículo, valida elegibilidade e gera feedback. Projeto de aprendizado, construído por fases (`requirements.txt` documenta cada uma, Fase 0 a Fase 10).

**Status atual:** pipeline principal funcional e testado de ponta a ponta: `POST /cv/analyze` extrai o currículo, valida elegibilidade, gera feedback, roda um agente juiz (Fase 10, LLM-as-judge) sobre o resultado e persiste tudo no Mongo via fila Celery/Redis.

RAG está conectado: cada análise é indexada no Qdrant ao final da task, e o chat pós-análise (Fase 9, `POST /chat/{session_id}`) usa esse índice pra responder perguntas sobre o resultado — mas é stateless por request (sem checkpointer; o cliente reenvia o histórico a cada chamada). Guardrails (Fase 3) cobrem só formato de arquivo e tamanho de texto extraído — prompt injection e PII ainda não têm checagem própria. Avaliação contínua (Fase 10) tem um dataset dourado e um harness básico (`app/evaluation/`), mas ainda não está em CI.

## Pré-requisitos

- Python 3.14
- Docker (Mongo e Redis locais)
- Chave de API da OpenAI

## 1. Ambiente virtual e dependências

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Variáveis de ambiente

Copia o exemplo e preenche a chave da OpenAI:

```bash
cp .env.example .env
```

Edita `.env` e preenche pelo menos:

```
OPENAI_API_KEY=sk-...
```

O resto (`MONGO_URI`, `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_BACKEND`, `QDRANT_URL`, etc.) já tem default apontando pra `localhost` em `app/core/config.py`, que já carrega o `.env` sozinho via `load_dotenv()` — não precisa exportar nada manualmente.

## 3. Subir o MongoDB (Docker)

```bash
docker run -d --name validador-mongo -p 27017:27017 -v mongo_validador_data:/data/db mongo:7
```

Se o container já existir, só inicia de novo:

```bash
sudo docker start validador-mongo
```

Confirma que a porta foi publicada (coluna `PORTS` deve mostrar `0.0.0.0:27017->27017/tcp`):

```bash
sudo docker ps
```

Testa a conexão:

```bash
python -m app.tests.db_tests.test_mongodb
```

> Se o `docker` sem `sudo` der "permission denied", seu usuário não está no grupo `docker` (`sudo usermod -aG docker $USER` e relogar resolve isso permanentemente).

## 4. Subir o Redis (Docker)

```bash
docker run -d --name validador-redis -p 6379:6379 redis:7
```

Redis serve dois papéis aqui: broker do Celery (carrega a mensagem da task da API pro worker) e result backend (guarda o resultado da task pra `/cv/status/{task_id}` consultar depois).

## 5. Subir o Qdrant (Docker)

```bash
docker run -d --name validador-qdrant -p 6333:6333 qdrant/qdrant
```

Usado pelo RAG: cada análise concluída é indexada aqui (`app/rag/ingest.py`) e consultada pelo chat pós-análise (`app/rag/retriever.py`). Se o Qdrant não estiver no ar, a análise principal e o chat continuam funcionando (elegibilidade/score vêm do Mongo) — só o contexto extra por critério fica indisponível.

## 6. Subir o worker Celery

Processo separado da API, terminal à parte:

```bash
celery -A app.worker.tasks worker --loglevel=info
```

Confere no banner de inicialização se aparece `results: redis://localhost:6379/0` (não `disabled://`) — confirma que o result backend tá ativo.

⚠️ **Atenção:** ao contrário do `uvicorn --reload`, o worker Celery **não recarrega código automaticamente**. Toda vez que mexer em `app/worker/tasks.py` (ou em qualquer módulo que ele importa: extractors, agentes, schemas), precisa `Ctrl+C` e subir o worker de novo.

## 7. Subir a API

```bash
uvicorn app.main:app --reload
```

API sobe em `http://localhost:8000`.

## 8. Testar o pipeline completo

O fluxo agora é assíncrono, em dois passos.

**a) Dispara a análise** — `POST /cv/analyze` espera `multipart/form-data` com dois campos:
- `file`: o arquivo do currículo (PDF ou DOCX)
- `job`: uma **string JSON** com os requisitos da vaga (schema `JobRequirements`)

Exemplo de JSON pro campo `job`:

```json
{
  "title": "Desenvolvedor Backend Python",
  "required_skills": ["Python", "FastAPI", "SQL"],
  "desired_skills": ["Docker", "AWS", "LangGraph"],
  "min_years_experience": 2,
  "min_education": "Superior completo em Ciência da Computação ou áreas afins"
}
```

Via curl (usando um dos PDFs de teste em `docs/` — `curriculo1.pdf` é um scan sem texto, usa outro pra não cair no guardrail):

```bash
curl -X POST http://localhost:8000/cv/analyze \
  -F "file=@docs/Curriculo-1.pdf" \
  -F 'job={"title":"Desenvolvedor Backend Python","required_skills":["Python","FastAPI","SQL"],"desired_skills":["Docker","AWS","LangGraph"],"min_years_experience":2,"min_education":"Superior completo em Ciência da Computação ou áreas afins"}'
```

Via Postman: `POST http://localhost:8000/cv/analyze`, Body → `form-data`, campo `file` como tipo **File**, campo `job` como tipo **Text** com o JSON acima.

Resposta (`202 Accepted`) vem na hora, sem esperar os LLMs:
```json
{"task_id": "...", "job_id": "..."}
```

**b) Consulta o resultado** — `GET /cv/status/{task_id}`:

```bash
curl http://localhost:8000/cv/status/<task_id>
```

Repete até `status` sair de `PENDING`/`STARTED` pra `SUCCESS` (ou `FAILURE`, com o motivo em `detail`). Quando `SUCCESS`, o `result` traz `job_id`, `resume_id`, `validation_id` (ids persistidos no Mongo) junto com `resume`, `validation` e `feedback`.

Pra conferir que persistiu de verdade, abre o Compass ou roda o script de teste e olha as coleções `jobs`, `resumes`, `validations` (e `judgements`, com a auditoria do agente juiz sobre esse resultado).

**c) Conversar sobre o resultado** — `POST /chat/{session_id}`, usando o `validation_id` retornado no passo anterior como `session_id`:

```bash
curl -X POST http://localhost:8000/chat/<validation_id> \
  -H "Content-Type: application/json" \
  -d '{"question": "Por que fui reprovado?", "messages": []}'
```

A resposta traz `answer` e a lista `messages` atualizada — reenvia essa lista no campo `messages` da próxima pergunta pra manter o histórico da conversa (não há checkpointer no servidor, o cliente é responsável por isso).

## 9. Rodar os testes

```bash
pytest app/tests
```

(alguns testes em `app/tests/db_tests` e `app/tests/api_tests` esperam Mongo/API rodando — não são só unit tests isolados)
