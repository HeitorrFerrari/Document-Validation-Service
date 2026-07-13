import json
import os

from langchain_openai import ChatOpenAI
from openai import OpenAI
from pydantic import BaseModel, Field
from app.schemas.schemas import CurriculoExtraido

_llm=ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("OPENAI_MAIN_MODEL"),
    temperature=float(os.getenv("OPENAI_TEMPERATURE")),
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extrair_curriculo(cv_texto: str) ->CurriculoExtraido:
    """
    Entrada:  cv_texto (str) -- texto bruto do currículo, já extraído
              de um PDF/DOCX (essa função não faz parsing de arquivo,
              só recebe texto puro).

    Saída:    um objeto CurriculoExtraido, validado contra o schema acima.
              Se o LLM tentar devolver algo fora do formato, a lib já
              lança erro de validação antes de chegar até você.
    """

    response = client.chat.completions.parse(
        model="gpt-4o-mini",
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
