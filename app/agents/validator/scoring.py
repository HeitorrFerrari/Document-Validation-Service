from datetime import datetime

from app.schemas.extracted_resume import CurriculoExtraido


def _parse_periodo(data_str: str) -> datetime:
    partes = data_str.split('-')
    ano = int(partes[0])
    mes = int(partes[1]) if len(partes) > 1 else 1
    return datetime(ano, mes, 1)


DATA_FIM_ATUAL = {"atual", "presente", "atualmente", "current", "present"}


def calcular_anos_experiencia(resume: CurriculoExtraido) -> float:
    total_meses = 0
    for exp in resume.experience:
        inicio = _parse_periodo(exp.data_inicio)
        data_fim_valida = exp.data_fim and exp.data_fim.strip().lower() not in DATA_FIM_ATUAL
        fim = _parse_periodo(exp.data_fim) if data_fim_valida else datetime.today()
        meses = (fim.year - inicio.year) * 12 + (fim.month - inicio.month)
        total_meses += max(meses, 0)
    return round(total_meses / 12, 1)
