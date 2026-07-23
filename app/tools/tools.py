from json import tool

from langchain_core.tools import Tools

@tool
def ask_infos(reason:str) -> dict:
    """Chame essa tool quando o currículo extraído não tiver informação
          suficiente pra avaliar elegibilidade (ex.: nenhuma experiência listada,
          nenhuma skill, formação vazia)."""
    return f"Informações insuficientes: {reason}"