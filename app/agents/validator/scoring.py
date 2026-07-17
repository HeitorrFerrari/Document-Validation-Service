from datetime import datetime

from app.schemas.extracted_resume import CurriculoExtraido


def _parse_periodo(data_str: str) -> datetime:
    partes = data_str.split('-')
    ano = int(partes[0])
    mes = int(partes[1]) if len(partes) > 1 else 1
    return datetime(ano, mes, 1)


def calcular_anos_experiencia(resume: CurriculoExtraido) -> float:
    total_meses = 0
    for exp in resume.experience:
        inicio = _parse_periodo(exp.data_inicio)
        fim = _parse_periodo(exp.data_fim) if exp.data_fim else datetime.today()
        meses = (fim.year - inicio.year) * 12 + (fim.month - inicio.month)
        total_meses += max(meses, 0)
    return round(total_meses / 12, 1)
