from pydantic import BaseModel, Field


class RequirementScore(BaseModel):
    requirement: str
    score: float = Field(ge=0, le=100)
    detail: str


class ValidationResult(BaseModel):
    is_eligible: bool
    score: float = Field(ge=0, le=100)
    requirement_scores: list[RequirementScore]
    reasoning: str
    resume_id: str | None
    job_id: str | None
