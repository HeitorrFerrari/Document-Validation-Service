"""
Harness de avaliação contínua / regressão do pipeline (Fase 10). Roda o
pipeline completo (app_graph) contra o dataset sintético de referência
(app/evaluation/dataset.py), compara score/elegibilidade com o esperado, e
usa o judge (app/judge/judge.py) como segunda checagem de consistência.
Serve de baseline pra medir se um ajuste de prompt melhorou ou piorou o
comportamento, em vez de julgar "no olho".

Roda como script manual (mesmo padrão de app/tests/graph_tests/test_graph.py)
-- não é um teste de CI, faz chamadas reais à API da OpenAI.
"""
from app.core.tracing import trace
from app.evaluation.dataset import DATASET, EvalCase
from app.graph.graph import app_graph
from app.judge.judge import evaluate as judge_evaluate
from app.schemas.validation_result import ValidationResult


def _checar_caso(caso: EvalCase, validation: ValidationResult) -> dict:
    score_ok = caso.score_esperado_min <= validation.score <= caso.score_esperado_max
    elegibilidade_ok = validation.is_eligible == caso.elegivel_esperado
    return {
        "caso": caso.nome,
        "score": validation.score,
        "score_esperado": f"{caso.score_esperado_min}-{caso.score_esperado_max}",
        "score_ok": score_ok,
        "elegivel": validation.is_eligible,
        "elegivel_esperado": caso.elegivel_esperado,
        "elegibilidade_ok": elegibilidade_ok,
        "passou": score_ok and elegibilidade_ok,
    }


def run_evaluation(dataset: list[EvalCase] = DATASET) -> list[dict]:
    resultados = []
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

        linha = _checar_caso(caso, validation)
        linha["judge_consistente"] = julgamento.is_consistent
        linha["judge_issues"] = julgamento.issues
        resultados.append(linha)

        trace("eval", "case_result", **{k: v for k, v in linha.items() if k != "judge_issues"})

    return resultados


def _imprimir_resumo(resultados: list[dict]) -> None:
    total = len(resultados)
    passaram = sum(1 for r in resultados if r["passou"])
    print(f"\n{passaram}/{total} casos dentro do esperado\n")

    for r in resultados:
        status = "OK" if r["passou"] else "FALHOU"
        print(
            f"[{status}] {r['caso']}: "
            f"score={r['score']} (esperado {r['score_esperado']}), "
            f"elegível={r['elegivel']} (esperado {r['elegivel_esperado']}), "
            f"judge_consistente={r['judge_consistente']}"
        )
        if r["judge_issues"]:
            print(f"        judge issues: {r['judge_issues']}")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    resultados = run_evaluation()
    _imprimir_resumo(resultados)
