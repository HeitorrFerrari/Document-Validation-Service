from bson import ObjectId
from bson.errors import InvalidId

from app.db.mongo import db
from app.schemas.validation_result import ValidationResult

collection = db["validations"]

def save_validation_result(validation_result: ValidationResult) -> str:
    validation = collection.insert_one(validation_result.model_dump())
    return str(validation.inserted_id)


def list_validations(limit: int = 50) -> list[dict]:
    """
    Lista as validações mais recentes pro histórico de conversas do front.
    Retorna dict cru (não `ValidationResult`) porque a view precisa do
    `session_id` (= `_id`) e da data de criação, que não estão no schema.
    O `_id` do Mongo carrega o timestamp de criação (`generation_time`).
    """
    documentos = collection.find().sort("_id", -1).limit(limit)
    sessoes = []
    for documento in documentos:
        oid = documento.pop("_id")
        sessoes.append({
            "session_id": str(oid),
            "created_at": oid.generation_time.isoformat(),
            "is_eligible": documento.get("is_eligible"),
            "score": documento.get("score"),
            "reasoning": documento.get("reasoning"),
            "requirement_scores": documento.get("requirement_scores", []),
            "resume_id": documento.get("resume_id"),
            "job_id": documento.get("job_id"),
        })
    return sessoes

def get_validation_result(validation_id: str) -> ValidationResult:
    try:
        oid = ObjectId(validation_id)
    except InvalidId:
        return None
    documento = collection.find_one({"_id": oid})
    if documento is None:
        return None
    documento.pop("_id")
    return ValidationResult(**documento)