from .DataBaseModel import DataBaseModel
from .Enums.CollectionValues import CollectionValues
from .DB_Schema.ErrorMessage import ErrorMessage
from bson import ObjectId

class ErrorQueryModel(DataBaseModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.ErrorCollection = self.db_client[CollectionValues.QUESTIONS.value]

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if CollectionValues.QUESTIONS.value not in all_collections:
            self.ErrorCollection = self.db_client[CollectionValues.QUESTIONS.value]
            indexes = ErrorMessage.get_indexes()
            for index in indexes:
                await self.ErrorCollection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index.get("unique", False)
                )

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def get_error_by_error_id(self, error_id: str):
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

        result = await self.ErrorCollection.insert_one(error.model_dump(
            by_alias=True,
            exclude_none=True
        ))

        error.id = result.inserted_id

        return error

    async def update_error(self, error_text: str, error_id: str):
        """
        Update the stored error_text for an existing error record.

        Fixed: previously built ErrorMessage(**updated_error) from the
        return value of update_one(), which is an UpdateResult object,
        not a document — that would have raised a TypeError on every
        call. Now re-fetches the actual updated document, same pattern
        JobProcessingModel already uses for its update methods.
        """
        result = await self.ErrorCollection.find_one(
            {"error_id": error_id}
        )

        if result is None:
            return None

        await self.ErrorCollection.update_one(
            {"error_id": error_id},
            {
                "$set": {
                    "error_text": error_text
                }
            }
        )

        updated_document = await self.ErrorCollection.find_one(
            {"error_id": error_id}
        )

        return ErrorMessage(**updated_document)

    async def get_or_create_error(self, error: ErrorMessage):
        result = await self.get_error_by_error_id(error.error_id)

        if result is None:
            result = await self.insert_error(error)
            return result

        return result

    async def delete_error(self, error_id: ObjectId):

        result = await self.ErrorCollection.delete_one(
            {
                "_id": error_id
            }
        )

        return result.deleted_count > 0