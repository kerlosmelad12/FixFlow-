from bson import ObjectId
from .DataBaseModel import DataBaseModel
from models.DB_Schema.Feedback import AnswerFeedback
from .Enums.CollectionValues import CollectionValues

class FeedbackModel(DataBaseModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.FeedbackCollection = self.db_client[CollectionValues.FEEDBACK.value]

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if CollectionValues.FEEDBACK.value not in all_collections:
                    self.FeedbackCollection = self.db_client[CollectionValues.FEEDBACK.value]
                    indexes = AnswerFeedback.get_indexes()
                    for index in indexes:
                        await self.FeedbackCollection.create_index(
                            index["key"],
                            name=index["name"],
                            unique=index.get("unique", False)
                        )
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def insert_feedback(self, feedback:AnswerFeedback):
        document = feedback
        result = await self.FeedbackCollection.insert_one(document)
        feedback['id'] = str(result.inserted_id)
        return AnswerFeedback(**feedback)