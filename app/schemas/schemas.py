from pydantic import BaseModel
from pydantic import Field

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
