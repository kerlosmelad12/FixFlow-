from pydantic import BaseModel,Field,validator
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

class Answer(BaseModel):
    id: Optional[ObjectId]=Field(None, alias="_id") # toto  solve the problem about private _id

    # to ignore any not commen datatypes for pydantic
    class Config :
        arbitrary_types_allowed=True
        allow_population_by_field_name = True

    
