from pydantic import BaseModel, Field, ConfigDict, field_serializer
from typing import Optional, List
from bson import ObjectId
from datetime import datetime


class Answer(BaseModel):

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    id: Optional[ObjectId] = Field(default=None, alias="_id")
    error_id: ObjectId
    job_id: Optional[ObjectId] = None

    error_type: str = Field(..., min_length=1)
    root_cause: str = Field(..., min_length=1)
    explanation: str = Field(..., min_length=1)
    solution: str = Field(..., min_length=1)

    steps: List[str] = Field(default_factory=list)
    code_fix: Optional[str] = None

    alternative_solutions: List[str] = Field(default_factory=list)

    recommendations: List[str] = Field(default_factory=list)
    confidence: Optional[float] = None
    sources: List[dict] = Field(default_factory=list)

    missing_information: List[str] = Field(default_factory=list)

    version: int = 1

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # FIX: ObjectId isn't JSON-serializable on its own. This serializer only
    # kicks in for mode="json" dumps (i.e. API responses) - plain
    # model_dump() calls used for Mongo writes still get a real ObjectId,
    # which is what Motor/PyMongo expects.
    @field_serializer("id", "error_id", "job_id", when_used="json")
    def _serialize_object_id(self, value: Optional[ObjectId]) -> Optional[str]:
        return str(value) if value is not None else None

    @classmethod
    def get_indexes(cls):

        return [
            {
                "key": [
                    ("error_id", 1)
                ],
                "name": "error_id_unique",
                "unique": True
            },

            {
                "key": [
                    ("job_id", 1)
                ],
                "name": "job_id_index",
                "unique": False
            }
        ]