"""
Rota de avaliação contínua (Fase 10): dispara o harness contra o dataset de
referência sob demanda. Endpoint interno de desenvolvimento -- cada chamada
roda o pipeline completo (~4 chamadas LLM por caso do dataset), não é pra
ficar exposto sem controle de custo/acesso fora de ambiente de dev.
"""
from fastapi import APIRouter

from app.evaluation.evaluation import run_evaluation, salvar_resultado
from app.schemas.eval_result import EvalRunResult

router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.post("/run", response_model=EvalRunResult)
async def run():
    resultado = run_evaluation()
    salvar_resultado(resultado)
    return resultado
