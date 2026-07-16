import json

from dotenv import load_dotenv

load_dotenv()

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

job = {
    "title": "Desenvolvedor Backend Pleno",
    "required_skills": ["Python", "SQL", "Git"],
    "desired_skills": ["Docker", "FastAPI"],
    "min_years_experience": 2,
    "min_education": "Graduação em Ciência da Computação ou correlatas",
}

if __name__ == "__main__":
    caminho = "docs/Curriculo Heitor - 2026.pdf"
    with open(caminho, "rb") as f:
        response = client.post(
            "/cv/analyze",
            files={"file": (caminho, f, "application/pdf")},
            data={"job": json.dumps(job)},
        )
    print("status:", response.status_code)
    print(response.json())
