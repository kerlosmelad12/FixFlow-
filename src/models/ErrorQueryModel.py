from .DataBaseModel import DataBaseModel
from .Enums.CollectionValues import CollectionValues
from .DB_Schema.ErrorQuery import ErrorQuery
class ErrorQueryModel(DataBaseModel):
       
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.ErrorCollection=self.db_client[CollectionValues.QUESTIONS.value]

    async def get_or_create(self,error_id:str):
        pass

        
