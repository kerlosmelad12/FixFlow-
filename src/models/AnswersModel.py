from .DataBaseModel import DataBaseModel
from .Enums.CollectionValues import CollectionValues
from .DB_Schema.Answer import Answer
from bson import ObjectId
from datetime import datetime


class AnswersModel(DataBaseModel):

    def __init__(self, db_client: object):

        super().__init__(db_client=db_client)

        self.AnswerCollection = self.db_client[CollectionValues.ANSWERS.value]

        self.AnswerHistoryCollection = self.db_client[CollectionValues.ANSWERS_HISTORY.value]

    async def init_collection(self):

        indexes = Answer.get_indexes()

        for index in indexes:
            await self.AnswerCollection.create_index(
                index["key"],
                name=index["name"],
                unique=index.get("unique", False)
            )

        await self.AnswerHistoryCollection.create_index(
            [("error_id", 1)],
            name="answer_history_error_id_index",
            unique=False
        )

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def insert_answer(self, answer: Answer):

        document = answer.model_dump(by_alias=True, exclude_none=True)

        result = await self.AnswerCollection.insert_one(document)

        answer.id = result.inserted_id

        return answer

    async def get_answer_by_error_id(self, error_id: ObjectId):

        document = await self.AnswerCollection.find_one({"error_id": error_id})


        if document is None:
            return None

        return Answer(**document)

    async def get_answer_by_id(self, answer_id: ObjectId):

        document = await self.AnswerCollection.find_one({"_id": answer_id})

        if document is None:
            return None

        return Answer.model_validate(document)

    async def update_answer(self, error_id: ObjectId, answer_data: dict):

        current = await self.AnswerCollection.find_one({"error_id": error_id})

        if current is not None:
            archived = dict(current)
            archived["archived_at"] = datetime.utcnow()
          
            archived.pop("_id", None)

            try:
                await self.AnswerHistoryCollection.insert_one(archived)
            except Exception:
             
                pass

        answer_data = dict(answer_data)
        answer_data["updated_at"] = datetime.utcnow()

        result = await self.AnswerCollection.update_one(
            {"error_id": error_id},
            {
                "$set": answer_data,
                "$inc": {"version": 1}
            }
        )

        return result

    async def get_answer_history(self, error_id: ObjectId):
  
        cursor = self.AnswerHistoryCollection.find(
            {"error_id": error_id}
        ).sort("archived_at", 1)

        return [Answer(**doc) async for doc in cursor]

    async def delete_answer(self, error_id: ObjectId):

        return await self.AnswerCollection.delete_one({"error_id": error_id})
    

    async def delete_by_error_id(self, error_id: str):

        error_object_id = ObjectId(error_id)

        # Delete current answer
        result = await self.AnswerCollection.delete_one(
            {
                "error_id": error_object_id
            }
        )

        # Delete answer history
        history = await self.AnswerHistoryCollection.delete_many(
            {
                "error_id": error_object_id
            }
        )

        return {
            "answer_deleted": result.deleted_count,
            "history_deleted": history.deleted_count
        }