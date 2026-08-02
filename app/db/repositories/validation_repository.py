from bson import ObjectId

from app.db.mongo import db
from app.schemas.validation_result import ValidationResult

collection = db["validations"]

def save_validation_result(validation_result: ValidationResult) -> str:
    validation = collection.insert_one(validation_result.model_dump())
    return str(validation.inserted_id)

def get_validation_result(validation_id: str) -> ValidationResult:
    documento = collection.find_one({"_id": ObjectId(validation_id)})
    if documento is None:
        return None
    documento.pop("_id")
    return ValidationResult(**documento)