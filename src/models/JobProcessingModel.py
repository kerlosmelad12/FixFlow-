from bson.objectid import ObjectId
from pymongo.errors import DuplicateKeyError
from .DataBaseModel import DataBaseModel
from .Enums.CollectionValues import CollectionValues
from .DB_Schema.ProcessingJob import ProcessingJob
from .Enums.JobProcessingEnums import JobProcessingEnums
from models.DB_Schema.ErrorMessage import ErrorMessage


class JobProcessingModel(DataBaseModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.JobsCollection = self.db_client[CollectionValues.JOBS.value]

    async def init_collection(self):

        all_collections = await self.db_client.list_collection_names()

        if CollectionValues.JOBS.value not in all_collections:
            indexes = ProcessingJob.get_indexes()

            for index in indexes:
                await self.JobsCollection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index.get("unique", False)
                )

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def create_job(self, job: ProcessingJob):
        """
        Insert a new job. If another request already inserted a job for the
        same error_message_id in the meantime (race condition between the
        existence-check in the route and this insert), we don't crash —
        we fetch and return the job that actually won the race.
        """
        try:
            result = await self.JobsCollection.insert_one(
                job.dict(by_alias=True, exclude_unset=True)
            )
            job.id = result.inserted_id
            return job

        except DuplicateKeyError:
            existing = await self.JobsCollection.find_one(
                {"error_message_id": job.error_message_id}
            )

            if existing is None:
                raise

            return ProcessingJob(**existing)

    async def get_job(self, error_message_id: str):
        try:
            error_message_id = ObjectId(error_message_id)
        except Exception:
            return None

        result = await self.JobsCollection.find_one(
            {"error_message_id": error_message_id}
        )

        if result is None:
            return None

        return ProcessingJob(**result)

    async def get_job_by_id(self, job_id: str):
        try:
            job_id = ObjectId(job_id)
        except Exception:
            return None

        result = await self.JobsCollection.find_one({"_id": job_id})

        if result is None:
            return None

        return ProcessingJob(**result)

    async def save_answer_results(self, error_message_id: str, results):

        job = await self.get_job(str(error_message_id))

        if job is None:
            return None

        await self.JobsCollection.update_one(
            {"_id": job.id},
            {"$set": {"answer_result": results}}
        )

        return await self.get_job_by_id(str(job.id))

    async def get_answer_results(self, error_message_id: str):

        job = await self.get_job(error_message_id)

        if job is None:
            return None

        answer = job.answer_result

        if not answer:
            return None

        return answer

    async def update_status(self, error_message_id: str, status: str):

        job = await self.get_job(str(error_message_id))

        if job is None:
            return None

        await self.JobsCollection.update_one(
            {"_id": job.id},
            {"$set": {"status": status}}
        )

        return await self.get_job_by_id(str(job.id))

    async def delete_by_error_id(self, error_id: str):

        error_object_id = ObjectId(error_id)

        result = await self.JobsCollection.delete_one(
            {
                "error_message_id": error_object_id
            }
        )

        return result.deleted_count

    