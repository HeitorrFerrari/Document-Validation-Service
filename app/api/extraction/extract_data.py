from openai import OpenAI

from app.core.config import settings
from app.schemas.extracted_resume import CurriculoExtraido

client = OpenAI(api_key=settings.openai_api_key)


def extrair_curriculo(cv_texto: str) -> CurriculoExtraido:
    """
    Entrada:  cv_texto (str) -- texto bruto do currículo, já extraído
              de um PDF/DOCX (essa função não faz parsing de arquivo,
              só recebe texto puro).

    Saída:    um objeto CurriculoExtraido, validado contra o schema acima.
              Se o LLM tentar devolver algo fora do formato, a lib já
              lança erro de validação antes de chegar até você.
    """
    response = client.chat.completions.parse(
        model=settings.openai_main_model,
        temperature=settings.openai_temperature,
        messages=[
            {
                "role": "system",
                "content": (
                    "Você extrai informações estruturadas de currículos. "
                    "Extraia APENAS o que está explicitamente no texto — "
                    "nunca invente datas, empresas ou skills que não "
                    "aparecem."
                ),
            },
            {"role": "user", "content": cv_texto},
        ],
        response_format=CurriculoExtraido,
    )
    return response.choices[0].message.parsed
