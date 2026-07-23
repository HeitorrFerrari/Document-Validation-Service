from typing import Optional, TypedDict

from app.schemas.extracted_resume import CurriculoExtraido
from app.schemas.validation_result import ValidationResult
from app.schemas.job_requirements import JobRequirements

class GraphState(TypedDict):
    resume_text: str
    job_requirements: JobRequirements
    resume: Optional[CurriculoExtraido]
    validation: Optional[ValidationResult]
    feedback: Optional[str]
    need_more_infos: Optional[bool]