from langsmith.wrappers import _openai
from openai import OpenAI, embeddings
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


def ingest_session(
        session_id: str,
        resume: CurriculoExtraido,
        job_requirements: JobRequirements,
        validation: ValidationResult,
) -> None:
    client = get_qdrant_client()

    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            COLLECTION_NAME,
            vectors_config=VectorParams(size=VECTOR_SIZE),
        )

        textos = _build_chunks(resume, job_requirements, validation)
        embbeddings = _openai.embeddings.create(model="text-embedding-3-small", input=textos)

        pontos = [
            PointStruct(
                id=f"{session_id}-{i}",
                vector=emb.embedding,
                payload={"session_id": session_id, "text": texto},
            )
            for i, (texto, emb) in enumerate(zip(textos, embeddings.data))
        ]
        client.upsert(COLLECTION_NAME, points=pontos)

    def delete_session(session_id: str) -> None:
        client = get_qdrant_client()
        client.delete(
            COLLECTION_NAME,
            points_selector=Filter(
                must=[FieldCondition(key="session_id", match=MatchValue(value=session_id))]
            ),
        )