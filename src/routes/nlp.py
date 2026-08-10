from fastapi import APIRouter,Depends,status,Request
from fastapi.responses import JSONResponse
from .schema.nlp import SimilarErrorsRequest
from models.ErrorQueryModel import ErrorQueryModel
from models.JobProcessingModel import JobProcessingModel
from models.Enums.ErrorEnums import ErrorEnums
from controllers.WebscearchController import WebscearchController
from controllers.NlpController import NlpController
from models.Enums.RetriveTypeEnums import RetriveTypeEnums
from models.Enums.JobProcessingEnums import JobProcessingEnums

nlp_app=APIRouter(
     prefix="/Fixflow-V1/nlp",
              tags=['nlp','V1']
)


@nlp_app.post("/similar/{error_id}")
async def get_similar_errors(error_id: str,res: Request,user_input: SimilarErrorsRequest):

    error_model = await ErrorQueryModel.create_instance(
        res.app.db_client
    )

    job_model = await JobProcessingModel.create_instance(
        res.app.db_client
    )

    nlp_controller = NlpController(
        classifier_client=res.app.classifier,
        vector_store_client=res.app.vectordb,
        generation_client=res.app.generation,
        embedding_client=res.app.embedding,
        templete_client=res.app.templete_parser
    )

  

    error = await error_model.get_error_by_error_id(
        error_id=error_id
    )

    if error is None:

        return JSONResponse(
            status_code=404,
            content={
                "result": ErrorEnums.ERROR_NOT_FOUND.value
            }
        )


    cache_result = await job_model.get_cached_search_result(
        error
    )

    if cache_result is not None:

        return JSONResponse(
            content={
                "kind": RetriveTypeEnums.CACHED.value,
                
                "result": [item.model_dump() if hasattr(item, "model_dump") else item
                for item in cache_result[0:user_input.limit]] ,

                "signal": ErrorEnums.MATCHED_ERROR_FOUND.value
            }
        )



    web_search_controller = WebscearchController(
        scearch_backend=error.source
    )

    query = error.error_signature

    results = web_search_controller.search(
        query=query,
        pagesize=user_input.pagesize
    )


    scored = nlp_controller.rank_similar_web_results(
        query,
        results,
        user_input.min_similarity
    )

    if not scored:

        return JSONResponse(
            content={
                "result": ErrorEnums.NO_MATCHED_ERROR.value
            }
        )

    cached_job = await job_model.save_cached_results(
        error_message_id=str(error.id),
        results=scored
    )

    if cached_job is None:

        return JSONResponse(
            status_code=500,
            content={
                "result": "Failed to save cached results."
            }
        )

 
    updated_job = await job_model.update_status(
        error_message_id=str(error.id),
        status=JobProcessingEnums.SEARCHED.value
    )

    if updated_job is None:

        return JSONResponse(
            status_code=500,
            content={
                "result": "Failed to update job status."
            }
        )



    return JSONResponse(
        content={
            "kind": RetriveTypeEnums.WEB_SCEARCH.value,
            "result": [item.model_dump()
                 for item in scored[:user_input.limit]
            ],
            "signal": ErrorEnums.MATCHED_ERROR_FOUND.value,
            "status": updated_job.status
        }
    )
