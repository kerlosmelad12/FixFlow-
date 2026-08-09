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
    print("DEBUG generation client:", res.app.generation)


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
    error_id = data_controller.generate_error_id( cleaned_text=cleaned_text)


    error_message = ErrorMessage(
        error_id=error_id,
        raw_extracted_tags=extracted_tags,
        error_type=error_type,
        error_title=error_title,
        error_text=query,
        error_signature=error_signature,
    )


    inserted_error= await error_model.get_or_create_error(error=error_message)
    cluster=await cluster_model.get_or_create_cluster(cluster=cluster,error_id=str(inserted_error.id))
    inserted_error.cluster_id=str(cluster.id)

    job = ProcessingJob(
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
        }
    )


@data_app.post("/search/")
async def get_error_data(user_request: SearchQuery, res: Request):

    error_model = await ErrorQueryModel.create_instance(res.app.db_client)
    cluster_model = await ClusterModel.create_instance(res.app.db_client)

    # Search by cluster
    if user_request.cluster_name:

        cluster = await cluster_model.get_data_by_cluster(
            cluster_name=user_request.cluster_name,
        )

        if cluster is None:
            return JSONResponse(
                status_code=404,
                content={"result": ErrorEnums.CLUSTER_NOT_FOUNDED.value},
            )

        results = []

        error_ids=[str(error_id) for error_id in cluster.error_ids]

        for error_id in error_ids[:user_request.limit] :
            error = await error_model.get_error_by_id(str(error_id))
            if error:
               error = error.copy()

               error["_id"] = str(error["_id"])

               results.append(jsonable_encoder(error))

        return JSONResponse(
            content={
                "result": ErrorEnums.ERROR_FOUND.value,
                "errors": results
            }
        )

    elif user_request.error_id:

        error = await error_model.get_error_by_error_id(
            user_request.error_id
        )

        if error is None:
            return JSONResponse(
                status_code=404,
                content={"result": ErrorEnums.ERROR_NOT_FOUND.value},
            )

        return JSONResponse(
            content={
                "result": ErrorEnums.ERROR_FOUND.value,
                "error": error.model_dump()
            }
        )

    return JSONResponse(
        status_code=400,
        content={
            "result": "Please provide either cluster_name or error_id."
        }
    )