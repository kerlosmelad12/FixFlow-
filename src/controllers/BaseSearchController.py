from abc import ABC, abstractmethod
from .BaseController import BaseController
from models.DB_Schema.Weabscearch import WeabscearchSearchResponse


class BaseSearchController(BaseController, ABC):
 

    @abstractmethod
    async def search(self, query: str, pagesize: int = 10) -> WeabscearchSearchResponse:
      
        ...