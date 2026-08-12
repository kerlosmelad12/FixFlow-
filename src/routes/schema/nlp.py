from pydantic import BaseModel, Field
from typing import Optional

class SimilarErrorsRequest(BaseModel):
    limit: int = Field(default=5, ge=1, le=20)
    min_similarity: float = Field(default=0.6, le=1.0)
    pagesize: int = Field(default=10, ge=1, le=50)

