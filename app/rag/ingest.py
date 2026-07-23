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
        chunks.append(
            f"Requisitos da vaga '{job_requirements.title}': "
            f"obrigatórios {job_requirements.required_skills}, "
            f"desejáveis {job_requirements.desired_skills}, "
            f"mín. {job_requirements.min_years_experience} anos de experiência"
        )

        for rs in validation.requirement_scores:
            chunks.append(
                f"Critério '{rs.requirement}': nota {rs.score}/100. {rs.detail}"
            )

        chunks.append(f"Nota final: {validation.score}/100. {validation.reasoning}")

        return chunks
