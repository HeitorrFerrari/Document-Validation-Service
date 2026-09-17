from bson import ObjectId
from bson.errors import InvalidId

from app.db.mongo import db
from app.schemas.job_requirements import JobRequirements

collection = db["jobs"]


def save_job(job: JobRequirements) -> str:
    resultado = collection.insert_one(job.model_dump())
    return str(resultado.inserted_id)

def get_job(job_id: str) -> JobRequirements | None:
    try:
        oid = ObjectId(job_id)
    except InvalidId:
        return None
    documento = collection.find_one({"_id": oid})
    if documento is None:
        return None
    documento.pop("_id")
    return JobRequirements(**documento)
