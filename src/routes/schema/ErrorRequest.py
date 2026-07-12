from pydantic import BaseModel, Field
from typing import Optional
class UserQueryRequest(BaseModel):
    query: str = Field(
        ...,
    )
    tags:list[str]=Field(...)
    programing_language:str=Field(...)

    
    
