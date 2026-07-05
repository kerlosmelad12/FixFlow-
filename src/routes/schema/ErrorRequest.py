from pydantic import BaseModel, Field
from typing import Optional
class UserQueryRequest(BaseModel):
    query: str = Field(
        ...,
    )
    tags:Optional[list]
    number_similer_questions:Optional[int]
    
