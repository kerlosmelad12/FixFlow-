from pydantic import BaseModel, Field
from typing import Optional
class UserQueryRequest(BaseModel):
    query: str = Field(
        ...
    )




class SearchQuery(BaseModel):
    cluster_name: str | None = None
    error_id: str | None = None
    limit: int = 5
    include_solutions: bool = True