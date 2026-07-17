from dotenv import load_dotenv

load_dotenv()

from app.db.repositories.job_repository import get_job, save_job
from app.schemas.job_requirements import JobRequirements

if __name__ == "__main__":
    job = JobRequirements(
        title="Desenvolvedor Backend Pleno",
        required_skills=["Python", "SQL", "Git"],
        desired_skills=["Docker", "FastAPI"],
        min_years_experience=2,
        min_education="Graduação em Ciência da Computação ou correlatas",
    )

    job_id = save_job(job)
    print("Salvo com id: ", job_id)

    job_recuperado = get_job(job_id)
    print(job_recuperado.model_dump_json(indent=2))
