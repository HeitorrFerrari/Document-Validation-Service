from app.db.mongo import db
from app.schemas.feedback import Feedback

collection = db["feedbacks"]


def save_feedback(feedback: Feedback) -> str:
    resultado = collection.insert_one(feedback.model_dump())
    return str(resultado.inserted_id)


def get_feedback(validation_id: str) -> Feedback | None:
    documento = collection.find_one({"validation_id": validation_id})
    if documento is None:
        return None
    documento.pop("_id")
    return Feedback(**documento)
