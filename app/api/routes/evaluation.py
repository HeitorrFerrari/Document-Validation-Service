"""
Rota de avaliação contínua (Fase 10): dispara o harness contra o dataset de
referência sob demanda. Endpoint interno de desenvolvimento -- cada chamada
roda o pipeline completo (~4 chamadas LLM por caso do dataset), não é pra
ficar exposto sem controle de custo/acesso fora de ambiente de dev.
"""
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.evaluation.evaluation import run_evaluation, salvar_resultado
from app.schemas.eval_result import EvalRunResult

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


class EvalRunRequest(BaseModel):
    ids: list[str] | None = None


@router.post("/run", response_model=EvalRunResult)
async def run(
    body: EvalRunRequest | None = None,
    ids: list[str] | None = Query(
        default=None,
        description="id(s) de caso do dataset pra rodar isolado (ex.: ?ids=match-forte). "
        "Vazio roda o dataset inteiro. Também aceito no body como {\"ids\": [...]}.",
    ),
):
    ids_alvo = ids or (body.ids if body else None)
    try:
        resultado = run_evaluation(ids=ids_alvo)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    salvar_resultado(resultado)
    return resultado
