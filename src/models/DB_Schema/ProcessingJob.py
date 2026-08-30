from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any
from bson.objectid import ObjectId
from datetime import datetime
import uuid
from ..Enums.JobProcessingEnums import JobProcessingEnums


class ProcessingJob(BaseModel):
    id: Optional[ObjectId] = Field(default=ObjectId, alias="_id")
    job_id: str = Field(default=lambda: str(uuid.uuid4()))
    status: str = JobProcessingEnums.PENDING.value
    error_message_id: Optional[ObjectId] = None
    error: Optional[str] = None
    created_at: datetime = Field(default=datetime.utcnow)
    updated_at: datetime = Field(default=datetime.utcnow)

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key": [("job_id", 1)],
                "name": "job_id_index_1",
                "unique": True
            },
            {
                "key": [("error_message_id", 1)],
                "name": "unique_error_message_job",
                "unique": True
            }
        ]

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}