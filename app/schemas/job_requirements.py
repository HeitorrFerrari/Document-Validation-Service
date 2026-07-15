from pydantic import BaseModel, Field


class JobRequirements(BaseModel):
    title: str
    required_skills: list[str]
    desired_skills: list[str] = Field(default_factory=list)
    min_years_experience: int
    min_education: str | None = None
