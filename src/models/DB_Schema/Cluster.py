from pydantic import BaseModel,Field,validator
from typing import Optional,List
from bson.objectid import ObjectId
import uuid

class Cluster(BaseModel):

    id: Optional[ObjectId] = Field(None, alias="_id")
    cluster_name: str = Field(default_factory=lambda: "Other")
    cluster_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    cluster_score: Optional[float] = None
    error_counts:int=0
    error_ids: Optional[List[ObjectId]] = []

    @classmethod
    def get_indexes(cls):
        return [
            {
                "key":[
                    ("cluster_name",1)
                ],
                "name":"cluster_name_index_1",
                "unique":True
            }
        ]

    class Config:
            arbitrary_types_allowed = True
            allow_population_by_field_name = True
            json_encoders = {ObjectId: str}
    
