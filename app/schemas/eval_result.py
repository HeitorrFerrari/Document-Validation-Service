from pydantic import BaseModel


class EvalCaseResult(BaseModel):
    caso: str
    score: float
    score_esperado_min: float
    score_esperado_max: float
    score_ok: bool
    elegivel: bool
    elegivel_esperado: bool
    elegibilidade_ok: bool
    judge_consistente: bool
    judge_issues: list[str]
    nota: float
    passou: bool


class EvalRunResult(BaseModel):
    executado_em: str
    nota_corte: float
    total_casos: int
    aprovados: int
    reprovados: int
    nota_media: float
    passou_geral: bool
    casos: list[EvalCaseResult]
