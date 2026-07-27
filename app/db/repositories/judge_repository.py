from app.db.mongo import db
from app.schemas.judge_result import JudgeResult

collection = db["judgements"]


def save_judgement(result: JudgeResult) -> str:
    resultado = collection.insert_one(result.model_dump())
    return str(resultado.inserted_id)


def get_judgement(validation_id: str) -> JudgeResult | None:
    documento = collection.find_one({"validation_id": validation_id})
    if documento is None:
        return None
    documento.pop("_id")
    return JudgeResult(**documento)
