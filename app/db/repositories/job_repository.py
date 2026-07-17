from bson import ObjectId
from app.db.mongo import db
from app.db.repositories.resume_repository import collection
from app.schemas.job_requirements import JobRequirements

collection = db["jobs"]

def save_job_requirements(resume: JobRequirements) -> str:
    job_requirements = collection.insert_one(resume.model_dump())
    return str(job_requirements.inserted_id)

def get_requirements(resume_id: str) -> JobRequirements:
    job_requirements = collection.find_one({"_id": ObjectId(resume_id)})
    if job_requirements is None:
        return None
    return JobRequirements(**job_requirements)