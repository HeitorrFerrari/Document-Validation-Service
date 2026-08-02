from pydantic import BaseModel, Field


class JudgeResult(BaseModel):
    is_consistent: bool
    issues: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    comment: str
    validation_id: str | None = None
