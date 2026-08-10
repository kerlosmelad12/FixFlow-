from pydantic import BaseModel,Field,validator
from typing import Optional,List
from bson.objectid import ObjectId
from datetime import datetime
from ..Enums.ErrorEnums import ErrorSource

class ErrorMessage(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    error_id:str=Field(...,min_length=1)

    error_title:str=Field(...,min_length=1)
    error_type: Optional[str] = None
    error_text: str = Field(..., min_length=1)
    error_signature: Optional[str] = None
    error_clean_text: str = Field(..., min_length=1)

    raw_extracted_tags: Optional[List[str]] = [] # All tags
    source: Optional[str] = ErrorSource.STACK_OVERFLOW.value             
    created_at: datetime = Field(default_factory=datetime.utcnow)
    answer_ids: Optional[List[ObjectId]] = []

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key":[
                    ("error_id",1)
                ],
                "name":"error_id_index_1",
                "unique":True
            }
        ]


    @validator("error_id")
    def validate_error_id(cls, val):
        if not val.replace("-", "").replace("_", "").isalnum():
            raise ValueError("error id must be alphanumeric (dashes/underscores allowed)")
        return val



    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
