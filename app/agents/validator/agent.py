from openai import OpenAI

from app.agents.validator.scoring import calcular_anos_experiencia
from app.core.config import settings
from app.prompts.base import build_system_prompt
from app.schemas.extracted_resume import CurriculoExtraido
from app.schemas.job_requirements import JobRequirements
from app.schemas.validation_result import ValidationResult

client = OpenAI(api_key=settings.openai_api_key)

_SYSTEM_PROMPT = build_system_prompt(
    "Você avalia se um candidato é elegível para uma vaga, "
    "comparando o currículo estruturado com os requisitos. "
    "Avalie CADA requisito da vaga (skills obrigatórias, skills "
    "desejáveis, anos de experiência e formação mínima) "
    "separadamente, com uma nota de 0 a 100 e um detalhe curto "
    "explicando o que no currículo comprova (ou não) aquele "
    "requisito especificamente. O score geral deve refletir a "
    "média ponderada dessas notas individuais. "
    "Para o requisito de anos de experiência, use o valor de "
    "'Anos de experiência (já calculado)' fornecido abaixo -- "
    "não estime a partir das datas brutas do currículo. "
    "Use APENAS as skills e experiências presentes no currículo "
    "-- nunca assuma competência que não está listada. "
    "Se a vaga tiver 'description', use-a como contexto qualitativo "
    "(senioridade esperada, responsabilidades, escopo) -- ela não é um "
    "critério pontuado à parte, mas pode ajudar a interpretar os demais."
)


def validate_eligibility(resume: CurriculoExtraido, job: JobRequirements) -> ValidationResult:
    """
    Entrada: currículo já estruturado (CurriculoExtraido) e os requisitos
             da vaga (JobRequirements).
    Saída:   ValidationResult com elegibilidade, score e justificativa,
             validado contra o schema -- o LLM não decide o formato, só o conteúdo.
    """
    anos_experiencia = calcular_anos_experiencia(resume)

    response = client.chat.completions.parse(
        model=settings.openai_main_model,
        temperature=settings.openai_temperature,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Currículo:\n{resume.model_dump_json()}\n\n"
                    f"Anos de experiência (já calculado): {anos_experiencia}\n\n"
                    f"Vaga:\n{job.model_dump_json()}"
                ),
            },
        ],
        response_format=ValidationResult,
    )
    return response.choices[0].message.parsed
