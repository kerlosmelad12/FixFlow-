from fastapi import APIRouter,Depends,status,Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from helper import get_settings
from models.Enums.JobProcessingEnums import JobProcessingEnums
from controllers.DataController import DataController
from .schema.data import UserQueryRequest,SearchQuery
from models.DB_Schema.ProcessingJob import ProcessingJob
from models.DB_Schema.ErrorMessage import ErrorMessage
from models.ErrorQueryModel import ErrorQueryModel
from models.JobProcessingModel import JobProcessingModel
from models.Enums.ErrorEnums import ErrorEnums
from controllers.NlpController import NlpController
from models.ClusterModel import ClusterModel
import uuid
from fastapi.encoders import jsonable_encoder

data_app=APIRouter(
    prefix="/Fixflow-V1/data",
          tags=['data','V1'])


# upload user query

# route
@data_app.post("/upload/")
async def upload_error_data(res: Request, error: UserQueryRequest ):

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
    
    extracted_error = nlp_controller.extract_error_details(query )
   

    if (not extracted_error or not extracted_error.get("success")):
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

    if not all([extracted_tags, error_type, error_title]):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"result": ErrorEnums.NO_EXTRAXTED_ERROR.value},
        )

    cleaned_text = extracted_error.get("cleaned_text")
    error_id = data_controller.generate_error_id( cleaned_text=cleaned_text)


    error_message = ErrorMessage(
        error_id=error_id,
        raw_extracted_tags=extracted_tags,
        error_type=error_type,
        error_title=error_title,
        error_text=query,
        error_signature=error_signature,
        error_clean_text=cleaned_text
    )


    inserted_error = await error_model.get_or_create_error(
        error=error_message
    )

    error_message_id = str(inserted_error.id)

    existing_job = await job_model.get_job(
        error_message_id
    )

    if existing_job is not None:

        if existing_job.status == JobProcessingEnums.SEARCHED.value:

            return JSONResponse(
                content={
                    "result": ErrorEnums.ERROR_FOUND.value,
                    "error_id": error_message.error_id,
                    "job_id": str(existing_job.id),
                    "status": existing_job.status,
                    "cached": True,
                    "data": [item.model_dump() if hasattr(item, "model_dump") else item
                for item in existing_job.cached_results]
                }
            )

        if existing_job.status in [
            JobProcessingEnums.PENDING.value,
            JobProcessingEnums.EXTRACTED.value
        ]:

            return JSONResponse(
                content={
                    "result": signal,
                    "error_id": error_message.error_id,
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
                    "result": signal,
                    "error_id": error_message.error_id,
                    "job_id": str(updated_job.id),
                    "status": updated_job.status,
                    "cached": False,
                    "retry": True
                }
            )

    cluster = nlp_controller.classify_text(
        query
    )
    cluster=await cluster_model.get_or_create_cluster(cluster=cluster,error_id=str(inserted_error.id))


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
            "error_id": error_message.error_id,
            "job_id": str(job.id),
            "cluster_name": cluster.cluster_name,
            "status": job.status,
            "cached": False
        }
    )

@data_app.get("/search/{error_id}")
async def get_error_data(error_id: str, res: Request):

    error_model = await ErrorQueryModel.create_instance(
        res.app.db_client
    )

    job_model = await JobProcessingModel.create_instance(
        res.app.db_client
    )


    error = await error_model.get_error_by_error_id(
        error_id
    )

    if error is None:

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "result": ErrorEnums.ERROR_NOT_FOUND.value,
                "error_id": error_id
            }
        )


    job = await job_model.get_job(
        str(error.id)
    )


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
                "status": job.status,
                "cached": False,
                "data": None
            }
        )



    if job.status == JobProcessingEnums.FAILED.value:

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "result": "Error processing failed.",
                "error_id": error_id,
                "job_id": str(job.id),
                "status": job.status,
                "cached": False,
                "data": None
            }
        )


    if job.status == JobProcessingEnums.SEARCHED.value:

        return JSONResponse(
            content=jsonable_encoder({
                "result": ErrorEnums.ERROR_FOUND.value,
                "error_id": error_id,
                "job_id": str(job.id),
                "status": job.status,
                "cached": True,
                "data": job.cached_results
            })
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