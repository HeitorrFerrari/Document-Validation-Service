from fastapi import APIRouter

from app.schemas.job_requirements import JobRequirements

router = APIRouter(prefix="/requirements", tags=["Requirements"])

@router.post("/", response_model=JobRequirements)
def extract_requirements(req: JobRequirements):

    return req