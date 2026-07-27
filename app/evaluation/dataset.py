"""
Dataset sintético de referência (Fase 10): pares currículo+vaga cobrindo
casos variados, com o resultado esperado definido manualmente. Base pro
harness de `evaluation.py` comparar contra -- serve de baseline antes de
qualquer ajuste de prompt.
"""
from dataclasses import dataclass

from app.schemas.job_requirements import JobRequirements


@dataclass
class EvalCase:
    nome: str
    resume_text: str
    job_requirements: JobRequirements
    score_esperado_min: float
    score_esperado_max: float
    elegivel_esperado: bool


DATASET: list[EvalCase] = [
    EvalCase(
        nome="match forte",
        resume_text="""
            Ana Beatriz Souza
            ana.souza@email.com

            Formação: Bacharelado em Ciência da Computação (concluído em 2019)

            Experiência:
            - Desenvolvedora Backend Pleno, Empresa TechCorp (2021 - atual)
              Desenvolvimento de APIs REST em Python com FastAPI, modelagem de banco
              PostgreSQL, containerização com Docker.
            - Desenvolvedora Backend Júnior, StartupX (2019 - 2021)
              Manutenção de sistema em Python/Django, testes automatizados com pytest.

            Skills: Python, FastAPI, Django, PostgreSQL, Docker, Git, pytest, SQL
        """,
        job_requirements=JobRequirements(
            title="Desenvolvedor(a) Backend Pleno",
            required_skills=["Python", "SQL", "Docker"],
            desired_skills=["FastAPI", "PostgreSQL"],
            min_years_experience=3,
            min_education="Ensino superior em Ciência da Computação ou áreas afins",
        ),
        score_esperado_min=75,
        score_esperado_max=100,
        elegivel_esperado=True,
    ),
    EvalCase(
        nome="match fraco",
        resume_text="""
            Carlos Eduardo Lima
            carlos.lima@email.com

            Formação: Bacharelado em Design Gráfico (concluído em 2020)

            Experiência:
            - Designer Gráfico Pleno, Agência Criativa (2020 - atual)
              Criação de identidade visual, peças pra redes sociais, uso de
              Photoshop, Illustrator e Figma.

            Skills: Photoshop, Illustrator, Figma, Branding, Direção de Arte
        """,
        job_requirements=JobRequirements(
            title="Engenheiro(a) de Dados",
            required_skills=["Python", "SQL", "Spark"],
            desired_skills=["Airflow", "AWS"],
            min_years_experience=2,
            min_education="Ensino superior em Ciência da Computação, Engenharia ou áreas afins",
        ),
        score_esperado_min=0,
        score_esperado_max=25,
        elegivel_esperado=False,
    ),
    EvalCase(
        nome="match parcial - só obrigatórias",
        resume_text="""
            Fernanda Alves Costa
            fernanda.costa@email.com

            Formação: Bacharelado em Sistemas de Informação (concluído em 2018)

            Experiência:
            - Analista de Dados Pleno, Empresa DataFlow (2019 - atual)
              Consultas SQL complexas, scripts de automação em Python,
              relatórios em Excel.

            Skills: Python, SQL, Excel, Power BI
        """,
        job_requirements=JobRequirements(
            title="Analista de Dados Sênior",
            required_skills=["Python", "SQL"],
            desired_skills=["Docker", "Kubernetes", "Airflow"],
            min_years_experience=4,
            min_education="Ensino superior em áreas relacionadas",
        ),
        score_esperado_min=35,
        score_esperado_max=65,
        elegivel_esperado=False,
    ),
    EvalCase(
        nome="borda - experiência exatamente no mínimo",
        resume_text="""
            Ricardo Nunes Pereira
            ricardo.pereira@email.com

            Formação: Bacharelado em Engenharia de Software (concluído em 2022)

            Experiência:
            - Desenvolvedor Backend, Empresa CodeBase (Janeiro de 2022 - atual)
              Desenvolvimento de APIs em Python, integração com bancos SQL.

            Skills: Python, SQL, Git
        """,
        job_requirements=JobRequirements(
            title="Desenvolvedor(a) Backend Júnior",
            required_skills=["Python", "SQL"],
            desired_skills=["Git"],
            min_years_experience=2,
            min_education="Ensino superior em áreas relacionadas",
        ),
        score_esperado_min=60,
        score_esperado_max=100,
        elegivel_esperado=True,
    ),
    EvalCase(
        nome="borda - formação abaixo do mínimo, resto forte",
        resume_text="""
            Juliana Martins Rocha
            juliana.rocha@email.com

            Formação: Ensino médio completo, cursos livres de programação (sem graduação)

            Experiência:
            - Desenvolvedora Backend Pleno, Empresa WebSystems (2020 - atual)
              APIs em Python/FastAPI, bancos PostgreSQL, Docker, CI/CD.
            - Desenvolvedora Backend Júnior, Freelancer (2018 - 2020)
              Projetos diversos em Python e Node.js.

            Skills: Python, FastAPI, PostgreSQL, Docker, Node.js, Git
        """,
        job_requirements=JobRequirements(
            title="Desenvolvedor(a) Backend Pleno",
            required_skills=["Python", "SQL", "Docker"],
            desired_skills=["FastAPI"],
            min_years_experience=3,
            min_education="Ensino superior completo em Ciência da Computação ou áreas afins",
        ),
        score_esperado_min=40,
        score_esperado_max=75,
        elegivel_esperado=False,
    ),
    EvalCase(
        nome="sem experiência - recém-formado pra vaga sênior",
        resume_text="""
            Pedro Henrique Alves
            pedro.alves@email.com

            Formação: Bacharelado em Ciência da Computação (concluído em 2024)

            Experiência:
            - Estagiário de Desenvolvimento, Empresa InicioTech (2023 - 2024)
              Apoio em tarefas de manutenção de sistema, testes manuais.

            Skills: Python, lógica de programação, Git (básico)
        """,
        job_requirements=JobRequirements(
            title="Engenheiro(a) de Software Sênior",
            required_skills=["Python", "arquitetura de sistemas distribuídos", "liderança técnica"],
            desired_skills=["Kubernetes", "AWS"],
            min_years_experience=6,
            min_education="Ensino superior em Ciência da Computação ou áreas afins",
        ),
        score_esperado_min=0,
        score_esperado_max=20,
        elegivel_esperado=False,
    ),
]
