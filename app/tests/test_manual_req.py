from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

payload = {
    "title": "Desenvolvedor Backend",
    "required_skills": ["Python", "SQL"],
    "desired_skills": ["Docker"],
    "min_years_experience": 2,
    "min_education": "Bacharelado em Ciência da Computação",
}

if __name__ == "__main__":
    response = client.post("/requirements/", json=payload)
    print("status:", response.status_code)
    print(response.json())
