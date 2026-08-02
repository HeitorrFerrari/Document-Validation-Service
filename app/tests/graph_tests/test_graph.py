from app.graph.graph import app_graph
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    from app.schemas.job_requirements import JobRequirements

    resultado = app_graph.invoke({
        "resume_text": "texto bruto do currículo aqui...",
        "job_requirements": JobRequirements(
            title="Dev Python",
            required_skills=["Python"],
            min_years_experience=1,
        ),
    })
    print(resultado["feedback"])
