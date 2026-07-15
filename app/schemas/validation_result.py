from pydantic import BaseModel, Field


class ValidationResult(BaseModel):
    is_eligible: bool
    score: float = Field(ge=0, le=100)
    met_requirements: list[str]
    missing_requirements: list[str]
    reasoning: str
