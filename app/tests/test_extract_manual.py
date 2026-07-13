from dotenv import load_dotenv

load_dotenv()

from app.api.extraction.extractData import extrair_curriculo

cv_exemplo = """
João da Silva
joao.silva@email.com

Experiência:
Empresa: TechCorp
Cargo: Desenvolvedor Backend
Início: 2021-03
Atual

Formação: Bacharelado em Ciência da Computação - USP

Skills: Python, FastAPI, SQL, Docker
"""

if __name__ == "__main__":
    resultado = extrair_curriculo(cv_exemplo)
    print(resultado.model_dump_json(indent=2))
