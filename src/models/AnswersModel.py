import logging
from .DataBaseModel import DataBaseModel
from .Enums.CollectionValues import CollectionValues
from .DB_Schema.Answer import Answer
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError

logger = logging.getLogger(__name__)


class AnswersModel(DataBaseModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)

        self.AnswerCollection = self.db_client[
            CollectionValues.ANSWERS.value
        ]

        self.AnswerHistoryCollection = self.db_client[
            CollectionValues.ANSWERS_HISTORY.value
        ]

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
        document = answer.model_dump(
            by_alias=True,
            exclude_none=True
        )

        result = await self.AnswerCollection.insert_one(document)

        answer.id = result.inserted_id

        return answer

    async def get_answer_by_error_id(self, error_id: str):
        document = await self.AnswerCollection.find_one(
            {"error_id": error_id}
        )

        if document is None:
            return None

        return Answer.model_validate(document)

    async def get_answer_by_id(self, answer_id):
        document = await self.AnswerCollection.find_one(
            {"_id": answer_id}
        )

        if document is None:
            return None

        return Answer.model_validate(document)

    async def archive_answer(self, error_id: str):
        current = await self.AnswerCollection.find_one(
            {"error_id": error_id}
        )

        if current is None:
            return None

        archived = dict(current)

        archived["archived_at"] = datetime.now(timezone.utc)

        archived.pop("_id", None)

        await self.AnswerHistoryCollection.insert_one(
            archived
        )

        return current

    async def delete_current_answer(self, error_id: str):
        return await self.AnswerCollection.delete_one(
            {"error_id": error_id}
        )

    async def update_answer(self, answer: Answer):

        error_id = answer.error_id

        current = await self.AnswerCollection.find_one(
            {"error_id": error_id}
        )

        if current is None:
            return None

        archived = dict(current)

        archived["archived_at"] = datetime.now(timezone.utc)

        archived.pop("_id", None)

        try:
            await self.AnswerHistoryCollection.insert_one(
                archived
            )
        except Exception:
            logger.exception(
                "Failed to archive answer history for error_id=%s", error_id
            )

        await self.AnswerCollection.delete_one(
            {"error_id": error_id}
        )

        return current

    async def save_answer(
        self,
        error_id: str,
        job_id: str | None,
        answer_fields: dict,
        force_refresh: bool = False
    ):

        existing = await self.get_answer_by_error_id(error_id)

        # Existing answer and no refresh
        if existing is not None and not force_refresh:
            return existing

        # Determine next version
        version = (
            existing.version + 1
            if existing is not None
            else 1
        )

        # Archive old answer
        if existing is not None:
            await self.update_answer(existing)

        new_answer = Answer(
            error_id=error_id,
            job_id=job_id,
            version=version,
            **answer_fields
        )

        try:
            return await self.insert_answer(new_answer)

        except DuplicateKeyError:

            # Another request inserted the same version.
            logger.exception(
                "Duplicate answer version for error_id=%s version=%s",
                error_id,
                version
            )

            # Get whatever is now stored
            current = await self.get_answer_by_error_id(
                error_id
            )

            if current is not None:
                return current

            raise

    async def get_answer_history(self, error_id: str):

        cursor = self.AnswerHistoryCollection.find(
            {"error_id": error_id}
        ).sort("archived_at", 1)

        return [
            Answer.model_validate(doc)
            async for doc in cursor
        ]

    async def delete_answer(self, error_id: str):

        return await self.AnswerCollection.delete_one(
            {"error_id": error_id}
        )

    async def delete_by_error_id(self, error_id: str):

        result = await self.AnswerCollection.delete_one(
            {"error_id": error_id}
        )

        history = await self.AnswerHistoryCollection.delete_many(
            {"error_id": error_id}
        )

        return {
            "answer_deleted": result.deleted_count,
            "history_deleted": history.deleted_count
        }