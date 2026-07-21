# Validador de Currículo

Pipeline de IA que recebe um currículo (PDF/DOCX) + os requisitos de uma vaga, extrai os dados do currículo, valida elegibilidade e gera feedback. Projeto de aprendizado, construído por fases (`requirements.txt` documenta cada uma, Fase 0 a Fase 10).

**Status atual:** Fase 8 (API) funcional com persistência no Mongo (Fase 6) plugada na rota `/cv/analyze`. RAG (Fase 4), fila assíncrona (Fase 7), tools do LangGraph (Fase 2/3) e avaliação contínua (Fase 10) ainda não implementados — os arquivos existem como stub.

## Pré-requisitos

- Python 3.14
- Docker (pra rodar o MongoDB local)
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

O resto (`MONGO_URI`, `REDIS_URL`, `QDRANT_URL`, etc.) já tem default apontando pra `localhost` em `app/core/config.py` — só precisa mudar se seus serviços locais rodarem em outra porta/host.

⚠️ **Pendência conhecida:** `app/core/config.py` ainda não chama `load_dotenv()`, então o `.env` não é carregado automaticamente ao rodar `uvicorn`. Até isso ser corrigido, exporte as variáveis manualmente antes de subir a API:

```bash
set -a
source .env
set +a
```

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

## 4. Subir a API

```bash
uvicorn app.main:app --reload
```

API sobe em `http://localhost:8000`.

## 5. Testar o pipeline completo

O endpoint `POST /cv/analyze` espera `multipart/form-data` com dois campos:
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

Via curl (usando um dos PDFs de teste em `docs/`):

```bash
curl -X POST http://localhost:8000/cv/analyze \
  -F "file=@docs/curriculo1.pdf" \
  -F 'job={"title":"Desenvolvedor Backend Python","required_skills":["Python","FastAPI","SQL"],"desired_skills":["Docker","AWS","LangGraph"],"min_years_experience":2,"min_education":"Superior completo em Ciência da Computação ou áreas afins"}'
```

Via Postman: `POST http://localhost:8000/cv/analyze`, Body → `form-data`, campo `file` como tipo **File**, campo `job` como tipo **Text** com o JSON acima.

A resposta traz `job_id` e `validation_id` (ids dos documentos salvos no Mongo) junto com `resume`, `validation` e `feedback`. Pra conferir que persistiu de verdade, abre o Compass ou roda o script de teste e olha as coleções `jobs`, `resumes`, `validations`.

## 6. Rodar os testes

```bash
pytest app/tests
```

(alguns testes em `app/tests/db_tests` e `app/tests/api_tests` esperam Mongo/API rodando — não são só unit tests isolados)
