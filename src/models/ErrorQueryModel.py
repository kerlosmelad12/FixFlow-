from .DataBaseModel import DataBaseModel
from .Enums.CollectionValues import CollectionValues
from .DB_Schema.ErrorMessage import ErrorMessage
class ErrorQueryModel(DataBaseModel):
       
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.ErrorCollection=self.db_client[CollectionValues.QUESTIONS.value]


    async def get_error(self,error_id:str):
        result = await self.ErrorCollection.find_one(
        {"error_id": error_id}
      )
        if not result:
            return None
        
        return ErrorMessage(**result)
    

    async def insert_error(self, error: ErrorMessage):

        result = await self.ErrorCollection.insert_one(error.dict(
        by_alias=True,
        exclude_none=True
        ))

        error.id = result.inserted_id

        return error
    
    async def update_error(self, error_text: str, error_id: str):
        result = await self.ErrorCollection.find_one(
        {"error_id": error_id}
      )

        if result:
           updated_error= await self.ErrorCollection.update_one(
            {"error_id": error_id},
            {
                "$set": {
                    "error_text": error_text
                }
            }
        )
           return ErrorMessage(**updated_error)

        return None
    

    



        
