"""
Harness de avaliação contínua / regressão do pipeline (Fase 10). Roda o
pipeline completo (app_graph) contra o dataset sintético de referência
(app/evaluation/dataset.py), compara score/elegibilidade com o esperado, usa
o judge (app/judge/judge.py) como segunda checagem de consistência, e
converte tudo numa nota 0-10 por caso. Caso com nota abaixo de NOTA_CORTE
reprova. Resultado persiste em JSON em app/evaluation/results/ -- não no
banco, é artefato de execução do harness, não dado de produto.

Roda como script manual (`python -m app.evaluation.evaluation`) ou via
POST /evaluation/run -- em ambos os casos faz chamadas reais à API da
OpenAI (dataset atual: 6 casos x ~4 chamadas cada).
"""
from datetime import datetime, timezone
from pathlib import Path

from app.core.tracing import trace
from app.evaluation.dataset import DATASET, EvalCase
from app.graph.graph import app_graph
from app.judge.judge import evaluate as judge_evaluate
from app.schemas.eval_result import EvalCaseResult, EvalRunResult
from app.schemas.judge_result import JudgeResult
from app.schemas.validation_result import ValidationResult

NOTA_CORTE = 7.5
_PESO_SCORE = 4.0
_PESO_ELEGIBILIDADE = 4.0
_PESO_JUDGE = 2.0

_PASTA_RESULTADOS = Path(__file__).parent / "results"


def _checar_caso(caso: EvalCase, validation: ValidationResult, julgamento: JudgeResult) -> EvalCaseResult:
    score_ok = caso.score_esperado_min <= validation.score <= caso.score_esperado_max
    elegibilidade_ok = validation.is_eligible == caso.elegivel_esperado

    nota = (
        (_PESO_SCORE if score_ok else 0.0)
        + (_PESO_ELEGIBILIDADE if elegibilidade_ok else 0.0)
        + (_PESO_JUDGE if julgamento.is_consistent else 0.0)
    )

    return EvalCaseResult(
        caso=caso.nome,
        score=validation.score,
        score_esperado_min=caso.score_esperado_min,
        score_esperado_max=caso.score_esperado_max,
        score_ok=score_ok,
        elegivel=validation.is_eligible,
        elegivel_esperado=caso.elegivel_esperado,
        elegibilidade_ok=elegibilidade_ok,
        judge_consistente=julgamento.is_consistent,
        judge_issues=julgamento.issues,
        nota=nota,
        passou=nota >= NOTA_CORTE,
    )


def _montar_resultado(casos: list[EvalCaseResult]) -> EvalRunResult:
    total = len(casos)
    aprovados = sum(1 for c in casos if c.passou)
    nota_media = round(sum(c.nota for c in casos) / total, 2) if total else 0.0

    return EvalRunResult(
        executado_em=datetime.now(timezone.utc).isoformat(),
        nota_corte=NOTA_CORTE,
        total_casos=total,
        aprovados=aprovados,
        reprovados=total - aprovados,
        nota_media=nota_media,
        passou_geral=aprovados == total,
        casos=casos,
    )


def run_evaluation(dataset: list[EvalCase] = DATASET) -> EvalRunResult:
    casos_resultado: list[EvalCaseResult] = []

    for caso in dataset:
        trace("eval", "run_case", caso=caso.nome)

        estado = app_graph.invoke({
            "resume_text": caso.resume_text,
            "job_requirements": caso.job_requirements,
            "resume": None,
            "validation": None,
            "feedback": None,
        })
        validation = estado["validation"]
        feedback = estado["feedback"]

        julgamento = judge_evaluate(estado["resume"], caso.job_requirements, validation, feedback)

        resultado_caso = _checar_caso(caso, validation, julgamento)
        casos_resultado.append(resultado_caso)

        trace(
            "eval", "case_result",
            caso=resultado_caso.caso,
            nota=resultado_caso.nota,
            passou=resultado_caso.passou,
        )

    return _montar_resultado(casos_resultado)


def salvar_resultado(resultado: EvalRunResult) -> Path:
    _PASTA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    nome_arquivo = f"eval_{resultado.executado_em.replace(':', '-')}.json"
    caminho = _PASTA_RESULTADOS / nome_arquivo
    caminho.write_text(resultado.model_dump_json(indent=2), encoding="utf-8")
    trace("eval", "salvo", caminho=str(caminho))
    return caminho


def _imprimir_resumo(resultado: EvalRunResult) -> None:
    print(
        f"\n{resultado.aprovados}/{resultado.total_casos} casos aprovados "
        f"(nota de corte {resultado.nota_corte}, nota média {resultado.nota_media})\n"
    )
    for c in resultado.casos:
        status = "OK" if c.passou else "REPROVOU"
        print(
            f"[{status}] {c.caso}: nota={c.nota}/10 | "
            f"score={c.score} (esperado {c.score_esperado_min}-{c.score_esperado_max}) | "
            f"elegível={c.elegivel} (esperado {c.elegivel_esperado}) | "
            f"judge_consistente={c.judge_consistente}"
        )
        if c.judge_issues:
            print(f"        judge issues: {c.judge_issues}")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    resultado = run_evaluation()
    caminho = salvar_resultado(resultado)
    _imprimir_resumo(resultado)
    print(f"\nResultado salvo em: {caminho}")
