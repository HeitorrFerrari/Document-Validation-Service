from bson import ObjectId

from app.db.mongo import db
from app.schemas.validation_result import ValidationResult

collection = db["validation"]