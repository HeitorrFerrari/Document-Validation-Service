from openai import OpenAI
from qdrant_client.models import Distance, PointStruct, VectorParams, Filter, FieldCondition, MatchValue

from app.rag.qdrant_client import get_qdrant_client, COLLECTION_NAME, VECTOR_SIZE
from app.schemas.extracted_resume import CurriculoExtraido
from app.schemas.job_requirements import JobRequirements
from app.schemas.validation_result import ValidationResult

def _build_chunks(
        resume: CurriculoExtraido,
        job_requirements: JobRequirements,
        validation: ValidationResult,
) -> list[str]:
    chunks = []

    for exp in resume.experience:
        chunks.append(
            f"Experiencia: {exp.cargo} na {exp.empresa}"
            f"({exp.data_inicio} - {exp.data_fim or 'atual'})"
        )

        chunks.append(f"Formação: {resume.graduation}")
        chunks.append(f"Skills do candidato: {', '.join(resume.skills)}")