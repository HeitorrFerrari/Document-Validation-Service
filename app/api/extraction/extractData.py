import json
import os

from langchain_openai import ChatOpenAI
from openai import OpenAI
from pydantic import BaseModel, Field

_llm=ChatOpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    model=os.getenv("OPENAI_MAIN_MODEL"),
    temperature=float(os.getenv("OPENAI_TEMPERATURE")),
)

class experience(BaseModel):
    empresa: str
    cargo: str
    data_inicio: str = Field(description="Formato AAAA-MM ou AAAA")
    data_fim: str = Field(description="Null se o emprego for atual")

class CurriculoExtraido(BaseModel):
    nome: str
    email: str
    experiencias: list[experience]
    skills: list[str]
    formacao: str

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

    response = _llm