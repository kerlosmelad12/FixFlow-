from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from .schema.nlp import SimilarErrorsRequest
from models.ErrorQueryModel import ErrorQueryModel
from models.JobProcessingModel import JobProcessingModel
from models.Enums.ErrorEnums import ErrorEnums
from controllers.SearchOrchestratorController import SearchOrchestratorController
from controllers.NlpController import NlpController
from models.Enums.RetriveTypeEnums import RetriveTypeEnums
from models.Enums.JobProcessingEnums import JobProcessingEnums
from models.DB_Schema.Weabscearch import WeabscearchSearchResponse
from groq import RateLimitError

nlp_app = APIRouter(
    prefix="/Fixflow-V1/nlp",
    tags=['nlp', 'V1']
)


@nlp_app.post("/similar/{error_id}")
async def get_similar_errors(error_id: str, res: Request, user_input: SimilarErrorsRequest):

    error_model = await ErrorQueryModel.create_instance(res.app.db_client)
    job_model = await JobProcessingModel.create_instance(res.app.db_client)

    nlp_controller = NlpController(
        classifier_client=res.app.classifier,
        vector_store_client=res.app.vectordb,
        generation_client=res.app.generation,
        embedding_client=res.app.embedding,
        templete_client=res.app.templete_parser
    )

    error = await error_model.get_error_by_error_id(error_id=error_id)

    if error is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"result": ErrorEnums.ERROR_NOT_FOUND.value}
        )

    cache_key = res.app.redis.build_search_cache_key(
        error_id=str(error.id),
        pagesize=user_input.pagesize,
        min_similarity=user_input.min_similarity,
        limit=user_input.limit
    )

    cache_result = await res.app.redis.get(cache_key)

    if cache_result is not None:
        return JSONResponse(
            content={
                "kind": RetriveTypeEnums.CACHED.value,
                "result": cache_result[0:user_input.limit],
                "signal": ErrorEnums.MATCHED_ERROR_FOUND.value
            }
        )

    query = error.error_title
    search_orchestrator = SearchOrchestratorController()

    results = await search_orchestrator.search_all_sources(
        query, user_input.pagesize, user_input.limit
    )

    scored = nlp_controller.rank_similar_web_results(
        error.error_text,
        results,
        user_input.min_similarity
    )

    if not scored:
        return JSONResponse(
            content={"result": ErrorEnums.NO_MATCHED_ERROR.value}
        )

    await res.app.redis.set(cache_key, scored)

    updated_job = await job_model.update_status(
        error_message_id=str(error.id),
        status=JobProcessingEnums.SEARCHED.value
    )

    if updated_job is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"result": ErrorEnums.FAIL_UPDATE_JOB.value}
        )

    return JSONResponse(
        content={
            "kind": RetriveTypeEnums.WEB_SCEARCH.value,
            "result": scored[:user_input.limit],
            "signal": ErrorEnums.MATCHED_ERROR_FOUND.value,
            "status": updated_job.status
        }
    )


@nlp_app.post("/answer/{error_id}")
async def answer_error_quetion(error_id: str, res: Request, user_input: SimilarErrorsRequest):

    error_model = await ErrorQueryModel.create_instance(res.app.db_client)
    job_model = await JobProcessingModel.create_instance(res.app.db_client)

    error = await error_model.get_error_by_error_id(error_id=error_id)

    if error is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"result": ErrorEnums.ERROR_NOT_FOUND.value}
        )

    error_message_id = str(error.id)

    saved_answer = await job_model.get_answer_results(error_message_id=error_message_id)

    if saved_answer is not None:
        return JSONResponse(
            content={
                "result": ErrorEnums.LLM_ANSWER_FOUND.value,
                "llm_response": saved_answer,
                "source": "job"
            }
        )

    query = error.error_signature

    search_cache_key = res.app.redis.build_search_cache_key(
        error_id=error_message_id,
        pagesize=user_input.pagesize,
        min_similarity=user_input.min_similarity,
        limit=user_input.limit
    )

    cached_results = await res.app.redis.get(search_cache_key)

    if cached_results is not None:
        results = WeabscearchSearchResponse(results=cached_results)
    else:
        search_orchestrator = SearchOrchestratorController()

        results = await search_orchestrator.search_all_sources(
            query=query,
            pagesize=user_input.pagesize,
            limit=user_input.limit
        )

        await res.app.redis.set(
            search_cache_key,
            results.model_dump()["results"]
        )

    nlp_controller = NlpController(
        classifier_client=res.app.classifier,
        vector_store_client=res.app.vectordb,
        generation_client=res.app.generation,
        embedding_client=res.app.embedding,
        templete_client=res.app.templete_parser
    )

    llm_result = nlp_controller.get_formatted_answer(
        error.error_text,
        results,
        min_similarity=user_input.min_similarity
    )

    if not llm_result.get("success"):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "result": ErrorEnums.THERE_NO_ANSWER.value,
                "error": llm_result.get("error"),
                "source": "llm"
            }
        )

    await job_model.update_status(
        error_message_id,
        status=JobProcessingEnums.ANSWERD.value
    )

    await job_model.save_answer_results(
        error_message_id=error_message_id,
        results=llm_result
    )

    return JSONResponse(
        content={
            "result": ErrorEnums.LLM_ANSWER_FOUND.value,
            "llm_response": llm_result,
            "system_prompt": llm_result.get("system_prompt"),
            "user_prompt": llm_result.get("user_prompt"),
            "source": "llm"
        }
    )