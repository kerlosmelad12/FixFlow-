from pydantic import BaseModel, Field
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

class AnswerFeedback(BaseModel):
    answer_id: str
    error_id: str
    rating: int = Field(default=1, ge=1, le=5)
    sentiment: str = Field(...)
    feedback_text: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("error_id", 1)],
                "name": "feedback_error_id_index",
                "unique": False
            }
        ]




