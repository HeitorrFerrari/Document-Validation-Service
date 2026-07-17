from app.db.mongo import db
from bson import ObjectId
from app.schemas.extracted_resume import CurriculoExtraido

collection = db["resumes"]

def save_resume(resume: CurriculoExtraido) -> str:
    resultado = collection.insert_one(resume.model_dump())
    return str(resultado.inserted_id)

def get_resume(resume_id: str) -> CurriculoExtraido | None:
    documento = collection.find_one({"_id": ObjectId(resume_id)})
    if documento is None:
        return None
    documento.pop("_id")