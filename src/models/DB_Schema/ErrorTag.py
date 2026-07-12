from pydantic import BaseModel,Field,validator
from typing import Optional,List
from bson.objectid import ObjectId
from datetime import datetime
from Enums.TagStatus import TagStatus
from Enums.TagsCategory import TagCategory

class ErrorTag(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    tag_name:str =Field(...,min_length=1)
    tag_alias:list[str]=[]
    status: TagStatus= TagStatus.PENDING.value
    category: Optional[str] = TagCategory.OTHER.value
    

    class Config:
        arbitrary_types_allowed = True
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}




    