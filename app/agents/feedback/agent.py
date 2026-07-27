from openai import OpenAI

from app.core.config import settings
from app.prompts.base import RH_PERSONA, build_system_prompt
from app.schemas.validation_result import ValidationResult

client = OpenAI(api_key=settings.openai_api_key)

_SYSTEM_PROMPT = build_system_prompt(
    f"{RH_PERSONA} "
    "Sua função aqui é redigir o texto de feedback que explica ao "
    "candidato o resultado da avaliação do currículo dele para a vaga, "
    "de forma clara e construtiva. "
    "Use APENAS as notas e detalhes fornecidos abaixo -- nunca "
    "invente, altere ou presuma informação que não esteja ali."
)


def build_feedback(result: ValidationResult) -> str:
    """
    Entrada: ValidationResult já calculado pelo agente validador.
    Saída:   texto em linguagem natural explicando a nota ao candidato --
             essa função não reavalia o currículo, só comunica a decisão
             que o validador já tomou.
    """
    response = client.chat.completions.create(
        model=settings.openai_main_model,
        temperature=settings.openai_temperature,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Resultado da avaliação:\n{result.model_dump_json()}",
            },
        ],
    )
    return response.choices[0].message.content
