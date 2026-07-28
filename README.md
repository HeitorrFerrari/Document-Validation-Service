# Validador de Currículo

Pipeline de IA que recebe um currículo (PDF/DOCX) e os requisitos de uma vaga, extrai os dados
estruturados do currículo, valida a elegibilidade do candidato e gera feedback textual. O
resultado pode ser conversado depois num chat que responde perguntas sobre a avaliação, e uma
auditoria automática (agente juiz) verifica a consistência da nota e do feedback gerados.

## O que a aplicação faz

1. Recebe currículo (PDF/DOCX) + descrição da vaga via API.
2. Valida o formato do arquivo e a qualidade do texto extraído (guardrails).
3. Extrai os dados do currículo (experiência, formação, skills) num schema estruturado.
4. Valida a elegibilidade do candidato contra os requisitos da vaga, com nota por critério.
5. Gera um feedback textual pro candidato a partir do resultado da validação.
6. Audita a própria avaliação com um agente juiz (LLM-as-judge), checando se a nota e o feedback
   são consistentes com o currículo e a vaga.
7. Indexa o resultado num banco vetorial (Qdrant), permitindo que o candidato converse sobre a
   avaliação depois — pergunte por que foi reprovado, peça detalhe por critério, etc.

Todo esse processamento roda em background (fila Celery/Redis) pra não travar a requisição HTTP;
o cliente dispara a análise, recebe um `task_id` na hora e consulta o resultado depois.

## Arquitetura

- **API** (`app/api/`) — recebe upload, dispara a fila, expõe consulta de status e chat.
- **Worker** (`app/worker/`) — task Celery que roda o pipeline completo em background.
- **Grafo de validação** (`app/graph/`) — orquestra extração → validação → feedback (LangGraph).
- **Agentes** (`app/agents/`) — validator (scoring) e feedback (geração de texto), ambos LLM.
- **Juiz** (`app/judge/`) — audita a saída dos agentes acima.
- **Chat** (`app/chats/`) — grafo separado que responde perguntas sobre uma análise já concluída.
- **RAG** (`app/rag/`) — chunking, embedding e busca vetorial (Qdrant) usados pelo chat.
- **Guard** (`app/guard/`) — validação de formato de arquivo e de texto extraído.
- **Db** (`app/db/`) — persistência em MongoDB (vaga, currículo, validação, auditoria do juiz).
- **Evaluation** (`app/evaluation/`) — dataset dourado e harness pra medir acurácia do pipeline.

## Limitações conhecidas

- O chat não tem memória no servidor: o histórico da conversa vai e volta no corpo da requisição,
  o cliente é responsável por reenviar as mensagens anteriores.
- Guardrails cobrem só formato de arquivo e tamanho do texto extraído — não há checagem dedicada
  de prompt injection ou PII.
- A task do worker é atômica: se o processo cair no meio, o reprocessamento é do zero (via retry
  da fila), não há retomada por etapa.
- O harness de avaliação contínua ainda roda manualmente, não está integrado a CI.

## Pré-requisitos

- Python 3.14
- Docker (Mongo, Redis e Qdrant locais)
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

O resto (`MONGO_URI`, `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_BACKEND`, `QDRANT_URL`, etc.) já
tem default apontando pra `localhost` em `app/core/config.py`, que já carrega o `.env` sozinho via
`load_dotenv()` — não precisa exportar nada manualmente.

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

> Se o `docker` sem `sudo` der "permission denied", seu usuário não está no grupo `docker`
> (`sudo usermod -aG docker $USER` e relogar resolve isso permanentemente).

## 4. Subir o Redis (Docker)

```bash
docker run -d --name validador-redis -p 6379:6379 redis:7
```

Redis serve dois papéis aqui: broker do Celery (carrega a mensagem da task da API pro worker) e
result backend (guarda o resultado da task pra `/cv/status/{task_id}` consultar depois).

## 5. Subir o Qdrant (Docker)

```bash
docker run -d --name validador-qdrant -p 6333:6333 qdrant/qdrant
```

Usado pelo RAG: cada análise concluída é indexada aqui (`app/rag/ingest.py`) e consultada pelo
chat pós-análise (`app/rag/retriever.py`). Se o Qdrant não estiver no ar, a análise principal e o
chat continuam funcionando (elegibilidade/score vêm do Mongo) — só o contexto extra por critério
fica indisponível.

## 6. Subir o worker Celery

Processo separado da API, terminal à parte:

```bash
celery -A app.worker.tasks worker --loglevel=info
```

Confere no banner de inicialização se aparece `results: redis://localhost:6379/0` (não
`disabled://`) — confirma que o result backend tá ativo.

⚠️ **Atenção:** ao contrário do `uvicorn --reload`, o worker Celery **não recarrega código
automaticamente**. Toda vez que mexer em `app/worker/tasks.py` (ou em qualquer módulo que ele
importa: extractors, agentes, schemas), precisa `Ctrl+C` e subir o worker de novo.

## 7. Subir a API

```bash
uvicorn app.main:app --reload
```

API sobe em `http://localhost:8000`.

## 8. Usando a aplicação

O fluxo é assíncrono, em três passos.

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

Via curl (usando um dos PDFs de teste em `docs/` — `curriculo1.pdf` é um scan sem texto, usa outro
pra não cair no guardrail):

```bash
curl -X POST http://localhost:8000/cv/analyze \
  -F "file=@docs/Curriculo-1.pdf" \
  -F 'job={"title":"Desenvolvedor Backend Python","required_skills":["Python","FastAPI","SQL"],"desired_skills":["Docker","AWS","LangGraph"],"min_years_experience":2,"min_education":"Superior completo em Ciência da Computação ou áreas afins"}'
```

Via Postman: `POST http://localhost:8000/cv/analyze`, Body → `form-data`, campo `file` como tipo
**File**, campo `job` como tipo **Text** com o JSON acima.

Resposta (`202 Accepted`) vem na hora, sem esperar os LLMs:
```json
{"task_id": "...", "job_id": "..."}
```

**b) Consulta o resultado** — `GET /cv/status/{task_id}`:

```bash
curl http://localhost:8000/cv/status/<task_id>
```

Repete até `status` sair de `PENDING`/`STARTED` pra `SUCCESS` (ou `FAILURE`, com o motivo em
`detail`). Quando `SUCCESS`, o `result` traz `job_id`, `resume_id`, `validation_id` (ids
persistidos no Mongo) junto com `resume`, `validation` e `feedback`.

Pra conferir que persistiu de verdade, abre o Compass ou roda o script de teste e olha as
coleções `jobs`, `resumes`, `validations` (e `judgements`, com a auditoria do agente juiz sobre
esse resultado).

**c) Conversa sobre o resultado** — `POST /chat/{session_id}`, usando o `validation_id` retornado
no passo anterior como `session_id`:

```bash
curl -X POST http://localhost:8000/chat/<validation_id> \
  -H "Content-Type: application/json" \
  -d '{"question": "Por que fui reprovado?", "messages": []}'
```

A resposta traz `answer` e a lista `messages` atualizada — reenvia essa lista no campo `messages`
da próxima pergunta pra manter o histórico da conversa (não há checkpointer no servidor, o cliente
é responsável por isso).

## 9. Rodar os testes

```bash
pytest app/tests
```

(alguns testes em `app/tests/db_tests` e `app/tests/api_tests` esperam Mongo/API rodando — não são
só unit tests isolados)
