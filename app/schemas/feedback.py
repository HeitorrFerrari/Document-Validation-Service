from pydantic import BaseModel


class Feedback(BaseModel):
    """
    Feedback redigido pro candidato ao fim do pipeline. Fica fora de
    `ValidationResult` de propósito: quem produz a nota é o agente validador,
    quem escreve o feedback é outro agente -- misturar os dois no mesmo schema
    obrigaria o validador a preencher um campo que não é dele.
    """
    text: str
    validation_id: str | None = None
