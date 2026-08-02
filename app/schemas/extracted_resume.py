from pydantic import BaseModel, EmailStr, Field


class Experience(BaseModel):
    empresa: str
    cargo: str
    data_inicio: str = Field(description="Formato AAAA-MM ou AAAA")
    data_fim: str | None = Field(default=None, description="Null se o emprego for atual")


class CurriculoExtraido(BaseModel):
    name: str
    email: EmailStr
    experience: list[Experience]
    skills: list[str]
    graduation: str
