from fastapi import APIRouter,Depends,status,Request
from fastapi.responses import JSONResponse
from helper import get_settings,Settings
from controllers.DataController import DataController
from controllers.ProcessController import ProcessController
from controllers.ProcessController import ProcessController
from .schema.ErrorRequest import UserQueryRequest
from models.DB_Schema.ProcessingJob import ProcessingJob
from models.DB_Schema.ErrorMessage import ErrorMessage
from models.ErrorQueryModel import ErrorQueryModel
from models.JobProcessingModel import JobProcessingModel
from models.Enums.ErrorEnums import ErrorEnums
from controllers.NlpController import NlpController
from models.ClusterModel import ClusterModel

data_app=APIRouter(
    prefix="/Fixflow-V1/data",
          tags=['data','V1'])


# upload user query

# route
@data_app.post("/upload/")
async def upload_error_data(res: Request, error: UserQueryRequest, app_setting=Depends(get_settings)):

    nlp_controller = NlpController(
        classifier_client=res.app.classifier,
        vector_store_client=res.app.vectordb,
        generation_client=res.app.generation,
        embedding_client=res.app.embedding,
    )
    print("DEBUG generation client:", res.app.generation)


    data_controller = DataController()
    error_model = ErrorQueryModel(res.app.db_client)
    job_model = JobProcessingModel(res.app.db_client)
    cluster_model = ClusterModel(res.app.db_client)

    query = error.query
    is_valid, signal = data_controller.validate_error(query)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"result": signal},
        )

   
    cluster = nlp_controller.classify_text(query)

    extracted_error = nlp_controller.extract_error_details(query)

    if not extracted_error or not extracted_error.get("success"):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"result": ErrorEnums.NO_EXTRAXTED_ERROR.value},
        )

    extracted_data = extracted_error.get("data")
    if not extracted_data:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"result": ErrorEnums.NO_EXTRAXTED_ERROR.value},
        )

    extracted_tags = extracted_data.get("tags")
    error_type = extracted_data.get("error_type")
    error_title = extracted_data.get("error_title")
    error_signature = extracted_data.get("error_signature")

    if not all([extracted_tags, error_type, error_title, error_signature]):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"result": ErrorEnums.NO_EXTRAXTED_ERROR.value},
        )

    cleaned_text = extracted_error.get("cleaned_text")
    error_id = data_controller.generate_error_id(error_title=error_title, cleaned_text=cleaned_text)


    error_message = ErrorMessage(
        error_id=error_id,
        raw_extracted_tags=extracted_tags,
        error_type=error_type,
        error_title=error_title,
        error_text=query,
        error_signature=error_signature,
    )



    inserted_error = await error_model.insert_error(error_message)
    _=await cluster_model.get_or_create_cluster(cluster=cluster,error_id=str(inserted_error.id))


    job = ProcessingJob(
        error_message_id=inserted_error.id,
        error=query,
    )
    job = await job_model.create_job(job)

    return JSONResponse(
        content={
            "result": signal,
            "error": extracted_data,
            "job_id": str(job.id),
        }
    )


@data_app.post("/process/")
async def process_error_data(user_request: UserQueryRequest):
    process_controller = ProcessController()
    return await process_controller.process_new_error(user_request)