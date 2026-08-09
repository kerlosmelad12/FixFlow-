from .DataBaseModel import DataBaseModel
from .Enums.CollectionValues import CollectionValues
from .DB_Schema.ErrorMessage import ErrorMessage
from bson import ObjectId

class ErrorQueryModel(DataBaseModel):
       
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.ErrorCollection=self.db_client[CollectionValues.QUESTIONS.value]

    async def init_collection(self):
        all_collections=await self.db_client.list_collection_names()
        if CollectionValues.QUESTIONS.value not in all_collections:
          self.ErrorCollection=self.db_client[CollectionValues.QUESTIONS.value] 
          indexes=ErrorMessage.get_indexes()
          for index in indexes:
                await self.ErrorCollection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index.get("unique", False)
                )
    @classmethod
    async def create_instance(cls,db_client:object):
        instance=cls(db_client)
        await instance.init_collection()
        return instance


    async def get_error_by_error_id(self,error_id:str):
        result = await self.ErrorCollection.find_one(
        {"error_id": error_id}
      )
        if not result:
            return None
        
        return ErrorMessage(**result)

    async def get_error_by_id(self, id: str):
        result = await self.ErrorCollection.find_one(
            {"_id": ObjectId(id)}
        )

        if result is None:
            return None

        return result
    

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

    async def get_or_create_error(self,error:ErrorMessage):
        result=await self.get_error_by_error_id(error.error_id)

        if result is None:
            result=await self.insert_error(error)
            return result

        return result

    

    



        
