"""
Agente LLM-as-judge (Fase 10): crítica independente da qualidade do
ValidationResult + feedback já produzidos pelo validator/feedback. Não
reavalia elegibilidade -- audita se a nota e o texto de feedback são
consistentes com o currículo e a vaga originais.
"""
from openai import OpenAI

from app.core.config import settings
from app.prompts.base import build_system_prompt
from app.schemas.extracted_resume import CurriculoExtraido
from app.schemas.job_requirements import JobRequirements
from app.schemas.judge_result import JudgeResult
from app.schemas.validation_result import ValidationResult

client = OpenAI(api_key=settings.openai_api_key)

_SYSTEM_PROMPT = build_system_prompt(
    "Você audita a qualidade de uma avaliação de currículo já feita por outro "
    "agente. Recebe o currículo, a vaga, o resultado da validação (notas e "
    "justificativa) e o texto de feedback enviado ao candidato. Verifique se "
    "as notas por critério são consistentes com o que o currículo realmente "
    "comprova, se o score geral reflete a média dos critérios, e se o texto "
    "de feedback não contradiz nem extrapola o resultado da validação. "
    "Liste em 'issues' cada inconsistência encontrada (vazio se não houver "
    "nenhuma). 'confidence' é o quão confiante você está na sua própria "
    "auditoria, não a nota do candidato."
)


def evaluate(
        resume: CurriculoExtraido,
        job: JobRequirements,
        validation: ValidationResult,
        feedback: str,
) -> JudgeResult:
    response = client.chat.completions.parse(
        model=settings.openai_main_model,
        temperature=settings.openai_temperature,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Currículo:\n{resume.model_dump_json()}\n\n"
                    f"Vaga:\n{job.model_dump_json()}\n\n"
                    f"Resultado da validação:\n{validation.model_dump_json()}\n\n"
                    f"Feedback enviado ao candidato:\n{feedback}"
                ),
            },
        ],
        response_format=JudgeResult,
    )
    return response.choices[0].message.parsed
