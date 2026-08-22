from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from models.Enums.JobProcessingEnums import JobProcessingEnums
from controllers.DataController import DataController
from .schema.data import UserQueryRequest
from models.DB_Schema.ProcessingJob import ProcessingJob
from models.DB_Schema.ErrorMessage import ErrorMessage
from models.ErrorQueryModel import ErrorQueryModel
from models.JobProcessingModel import JobProcessingModel
from models.Enums.ErrorEnums import ErrorEnums
from controllers.NlpController import NlpController
from models.ClusterModel import ClusterModel
from models.AnswersModel import AnswersModel
import uuid
import logging
from bson.objectid import ObjectId


logger = logging.getLogger(__name__)

data_app = APIRouter(
    prefix="/Fixflow-V1/data",
    tags=['data', 'V1'])


@data_app.post("/upload/")
async def upload_error_data(res: Request, error: UserQueryRequest):

    nlp_controller = NlpController(
        classifier_client=res.app.classifier,
        vector_store_client=res.app.vectordb,
        generation_client=res.app.generation,
        embedding_client=res.app.embedding,
        templete_client=res.app.templete_parser
    )

    data_controller = DataController()
    error_model = await ErrorQueryModel.create_instance(res.app.db_client)
    job_model = await JobProcessingModel.create_instance(res.app.db_client)
    cluster_model = await ClusterModel.create_instance(res.app.db_client)

    query = error.query
    is_valid, signal = data_controller.validate_error(query)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"result": signal},
        )

    try:
        extracted_error = nlp_controller.extract_error_details(query)
    except Exception as e:
        logger.exception("extract_error_details failed for query=%r", query)
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "result": ErrorEnums.NO_EXTRAXTED_ERROR.value,
                "error": "extraction_failed",
                "detail": str(e),
            }
        )

    if not extracted_error or not extracted_error.get("success"):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "result": ErrorEnums.NO_EXTRAXTED_ERROR.value
            }
        )

    extracted_data = extracted_error.get("data")

    if not extracted_data:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "result": ErrorEnums.NO_EXTRAXTED_ERROR.value
            }
        )

    extracted_tags = extracted_data.get("tags")
    error_type = extracted_data.get("error_type")
    error_title = extracted_data.get("error_title")
    error_signature = extracted_data.get("error_signature")


    logger.debug(
        "extracted tags=%s type=%s title=%s signature=%s",
        extracted_tags, error_type, error_title, error_signature
    )

    if not all([extracted_tags, error_type, error_title]):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"result": ErrorEnums.NO_EXTRAXTED_ERROR.value},
        )

    cleaned_text = extracted_error.get("cleaned_text")
    error_id = data_controller.generate_error_id(cleaned_text=cleaned_text)

    error_message = ErrorMessage(
        error_id=error_id,
        raw_extracted_tags=extracted_tags,
        error_type=error_type,
        error_title=error_title,
        error_text=query,
        error_signature=error_signature,
        error_clean_text=cleaned_text
    )

    try:
        existing_by_hash = await error_model.get_error_by_error_id(error_id)

        if existing_by_hash is not None:
            inserted_error = existing_by_hash

        else:
            duplicate_error_id = nlp_controller.find_duplicate_error(cleaned_text)

            existing_near_duplicate = (
                await error_model.get_error_by_error_id(duplicate_error_id)
                if duplicate_error_id
                else None
            )

            if existing_near_duplicate is not None:
                inserted_error = existing_near_duplicate

            else:
                inserted_error = await error_model.insert_error(error_message)

                # FIX: the return value was being discarded - now logged if
                # indexing failed, so a dedup outage is visible instead of
                # silently degrading.
                indexed = nlp_controller.index_error_for_dedup(inserted_error)

                if not indexed:
                    logger.warning(
                        "index_error_for_dedup failed for error_id=%s - this "
                        "error won't be dedup-matchable until backfilled",
                        inserted_error.error_id
                    )

    except Exception as e:
        logger.exception("DB error while creating/fetching error record")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"result": "Database error while saving the error record.", "detail": str(e)}
        )

    error_message_id = str(inserted_error.id)

    existing_job = await job_model.get_job(error_message_id)

    if existing_job is not None:

        if existing_job.status == JobProcessingEnums.SEARCHED.value:

            return JSONResponse(
                content={
                    "result": ErrorEnums.ERROR_FOUND.value,
                    "error_id": inserted_error.error_id,
                    "job_id": str(existing_job.id),
                    "status": existing_job.status,
                    "cached": True,
                }
            )

        if existing_job.status in [
            JobProcessingEnums.PENDING.value,
            JobProcessingEnums.EXTRACTED.value
        ]:

            return JSONResponse(
                content={
                    "result": ErrorEnums.ERROR_FOUND.value,
                    "error_id": inserted_error.error_id,
                    "job_id": str(existing_job.id),
                    "status": existing_job.status,
                    "cached": False
                }
            )

        if existing_job.status == JobProcessingEnums.FAILED.value:

            updated_job = await job_model.update_status(
                error_message_id=error_message_id,
                status=JobProcessingEnums.PENDING.value
            )

            return JSONResponse(
                content={
                    "result": ErrorEnums.ERROR_FOUND.value,
                    "error_id": inserted_error.error_id,
                    "job_id": str(updated_job.id),
                    "status": updated_job.status,
                    "cached": False,
                    "retry": True
                }
            )

    try:
        cluster = nlp_controller.classify_text(query)
        cluster = await cluster_model.get_or_create_cluster(
            cluster=cluster, error_id=str(inserted_error.id)
        )
    except Exception as e:
        logger.exception("classify_text/get_or_create_cluster failed for error_id=%s", error_message_id)
        job = ProcessingJob(
            job_id=str(uuid.uuid4()),
            error_message_id=inserted_error.id,
            error=query,
            status=JobProcessingEnums.PENDING.value
        )
        job = await job_model.create_job(job)

        return JSONResponse(
            status_code=status.HTTP_207_MULTI_STATUS,
            content={
                "result": signal,
                "error_id": inserted_error.error_id,
                "job_id": str(job.id),
                "cluster_name": None,
                "status": job.status,
                "cached": False,
                "warning": "classification_failed",
                "detail": str(e),
            }
        )

    job = ProcessingJob(
        job_id=str(uuid.uuid4()),
        error_message_id=inserted_error.id,
        error=query,
        status=JobProcessingEnums.PENDING.value
    )
    job = await job_model.create_job(job)

    return JSONResponse(
        content={
            "result": signal,
            "error_id": inserted_error.error_id,
            "job_id": str(job.id),
            "cluster_name": cluster.cluster_name,
            "status": job.status,
            "cached": False
        }
    )


@data_app.get("/search/{error_id}")
async def get_error_data(error_id: str, res: Request):

    error_model = await ErrorQueryModel.create_instance(res.app.db_client)
    job_model = await JobProcessingModel.create_instance(res.app.db_client)

    error = await error_model.get_error_by_error_id(error_id)

    if error is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "result": ErrorEnums.ERROR_NOT_FOUND.value,
                "error_id": error_id
            }
        )

    job = await job_model.get_job(str(error.id))

    if job is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "result": "No processing job found for this error.",
                "error_id": error_id
            }
        )

    if job.status in [
        JobProcessingEnums.PENDING.value,
        JobProcessingEnums.EXTRACTED.value
    ]:
        return JSONResponse(
            content={
                "result": "Error is still being processed.",
                "error_id": error_id,
                "job_id": str(job.id),
                "status": job.status
            }
        )

    if job.status == JobProcessingEnums.FAILED.value:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "result": "Error processing failed.",
                "error_id": error_id,
                "job_id": str(job.id),
                "status": job.status
            }
        )

    if job.status == JobProcessingEnums.SEARCHED.value:

        return JSONResponse(
            content={
                "result": ErrorEnums.ERROR_FOUND.value,
                "error_id": error_id,
                "job_id": str(job.id),
                "status": job.status
            }
        )

    if job.status == JobProcessingEnums.ANSWERD.value:
        return JSONResponse(
            content={
                "result": "Answer already generated for this error.",
                "error_id": error_id,
                "job_id": str(job.id),
                "status": job.status
            }
        )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "result": "Unknown job status.",
            "error_id": error_id,
            "job_id": str(job.id),
            "status": job.status
        }
    )


@data_app.delete("/error/{error_id}")
async def delete_error(error_id: str, res: Request):

    error_model = await ErrorQueryModel.create_instance(
        res.app.db_client
    )

    job_model = await JobProcessingModel.create_instance(
        res.app.db_client
    )

    answer_model = await AnswersModel.create_instance(
        res.app.db_client
    )

    cluster_model = await ClusterModel.create_instance(
        res.app.db_client
    )

    # Find error
    error = await error_model.get_error_by_error_id(
        error_id
    )
    error = await error_model.get_error_by_error_id(error_id)

    logger.debug("DELETE REQUEST error_id=%s", error_id)
    logger.debug("DELETE FOUND=%s", error)

    logger.info("DELETE ERROR ID = %s", error_id)
    logger.info("DELETE FOUND ERROR = %s", error)

    if error is None:
        return JSONResponse(
            status_code=404,
            content={
                "result": "ERROR_NOT_FOUND",
                "error_id": error_id
            }
        )

    error_db_id = str(error.id)

    # Delete answers history
    deleted_answers = await answer_model.delete_by_error_id(
        error_db_id
    )

    # Delete job
    deleted_job = await job_model.delete_by_error_id(
        error_db_id
    )

    # Delete cluster
    deleted_cluster = await cluster_model.delete_by_error_id(
        error_db_id
    )

    # Delete error
    deleted_error = await error_model.delete_by_error_id(
        error_id
    )

    return JSONResponse(
        content={
            "result": "ERROR_DELETED",
            "error_id": error_id,
            "deleted": {
                "error": deleted_error,
                "job": deleted_job,
                "answers": deleted_answers,
                "cluster": deleted_cluster
            }
        }
    )