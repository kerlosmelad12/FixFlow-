from pydantic import BaseModel, Field
from typing import Optional

class SimilarErrorsRequest(BaseModel):
    limit: int = 5
    min_similarity: float = 0.6
    pagesize:int=10