from fastapi import APIRouter, status, Request
from fastapi.responses import JSONResponse
from .schema.nlp import SimilarErrorsRequest
from models.ErrorQueryModel import ErrorQueryModel
from models.JobProcessingModel import JobProcessingModel
from models.AnswersModel import AnswersModel
from models.DB_Schema.Answer import Answer
from models.Enums.ErrorEnums import ErrorEnums
from controllers.SearchOrchestratorController import SearchOrchestratorController
from controllers.NlpController import NlpController
from models.Enums.RetriveTypeEnums import RetriveTypeEnums
from models.Enums.JobProcessingEnums import JobProcessingEnums
from models.DB_Schema.Weabscearch import WeabscearchSearchResponse
from groq import RateLimitError
import logging

logger = logging.getLogger(__name__)

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

    try:
        cache_result = await res.app.redis.get(cache_key)
    except Exception:
        logger.exception("Redis get failed for cache_key=%s", cache_key)
        cache_result = None

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

    try:
        results = await search_orchestrator.search_all_sources(
            query, user_input.pagesize, user_input.limit
        )
    except Exception as e:
        logger.exception("search_all_sources failed for error_id=%s", error_id)
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "result": "Search failed while looking for similar errors.",
                "error_id": error_id,
                "detail": str(e),
            }
        )

    try:
        scored = nlp_controller.rank_similar_web_results(
            error.error_text,
            results,
            user_input.min_similarity
        )
    except RateLimitError as e:
        logger.warning("Rate limited while ranking results for error_id=%s: %s", error_id, e)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "result": "Rate limit hit while ranking search results. Please try again shortly.",
                "error_id": error_id,
            }
        )
    except Exception as e:
        logger.exception("rank_similar_web_results failed for error_id=%s", error_id)
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "result": "Failed to rank search results.",
                "error_id": error_id,
                "detail": str(e),
            }
        )

    if not scored:
        return JSONResponse(
            content={"result": ErrorEnums.NO_MATCHED_ERROR.value}
        )

    try:
        await res.app.redis.set(cache_key, scored)
    except Exception:
        logger.exception("Redis set failed for cache_key=%s", cache_key)

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
async def answer_error_quetion( error_id: str, res: Request,
                                user_input: SimilarErrorsRequest, force_refresh: bool = False):
    """
    force_refresh=False (default): if an answer already exists for this
    error, return it as-is - no search, no LLM call.

    force_refresh=True: regenerate the answer even if one exists. The
    previous answer is archived (not lost) via AnswersModel.update_answer,
    and the version counter increments.
    """

    error_model = await ErrorQueryModel.create_instance(res.app.db_client)
    job_model = await JobProcessingModel.create_instance(res.app.db_client)
    answers_model = await AnswersModel.create_instance(res.app.db_client)

    error = await error_model.get_error_by_error_id(error_id=error_id)

    if error is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"result": ErrorEnums.ERROR_NOT_FOUND.value}
        )

    error_message_id = str(error.id)

    existing_answer = await answers_model.get_answer_by_error_id(error.id)


    if existing_answer is not None and not force_refresh:
        return JSONResponse(
            content={
                "result": ErrorEnums.LLM_ANSWER_FOUND.value,
                "llm_response": existing_answer.model_dump(
                    mode="json", by_alias=True, exclude_none=True
                ),
                "source": "db"
            }
        )

    query = error.error_signature

    search_cache_key = res.app.redis.build_search_cache_key(
        error_id=error_message_id,
        pagesize=user_input.pagesize,
        min_similarity=user_input.min_similarity,
        limit=user_input.limit
    )

    try:
        cached_results = await res.app.redis.get(search_cache_key)
    except Exception:
        logger.exception("Redis get failed for search_cache_key=%s", search_cache_key)
        cached_results = None

    if cached_results is not None:
        results = WeabscearchSearchResponse(results=cached_results)
    else:
        search_orchestrator = SearchOrchestratorController()

        try:
            results = await search_orchestrator.search_all_sources(
                query=query,
                pagesize=user_input.pagesize,
                limit=user_input.limit
            )
        except Exception as e:
            logger.exception("search_all_sources failed for error_id=%s", error_id)
            return JSONResponse(
                status_code=status.HTTP_502_BAD_GATEWAY,
                content={
                    "result": "Search failed while gathering context for the answer.",
                    "error_id": error_id,
                    "detail": str(e),
                }
            )

        try:
            await res.app.redis.set(
                search_cache_key,
                results.model_dump()["results"]
            )
        except Exception:
            logger.exception("Redis set failed for search_cache_key=%s", search_cache_key)

    nlp_controller = NlpController(
        classifier_client=res.app.classifier,
        vector_store_client=res.app.vectordb,
        generation_client=res.app.generation,
        embedding_client=res.app.embedding,
        templete_client=res.app.templete_parser
    )

    try:
        llm_result = nlp_controller.get_formatted_answer(
            error.error_text,
            results,
            min_similarity=user_input.min_similarity
        )
    except RateLimitError as e:
        logger.warning("Rate limited while generating answer for error_id=%s: %s", error_id, e)
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "result": "Rate limit hit while generating the answer. Please try again shortly.",
                "error_id": error_id,
            }
        )
    except Exception as e:
        logger.exception("get_formatted_answer failed for error_id=%s", error_id)
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "result": ErrorEnums.THERE_NO_ANSWER.value,
                "error": str(e),
                "source": "llm"
            }
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

    job = await job_model.get_job(error_message_id)

    answer_fields = {
        "error_type": llm_result.get("error_type") or "unknown",
        "root_cause": llm_result.get("root_cause") or "",
        "explanation": llm_result.get("explanation") or "",
        "solution": llm_result.get("solution") or "",
        "steps": llm_result.get("steps") or [],
        "code_fix": llm_result.get("code_fix"),
        "alternative_solutions": llm_result.get("alternative_solutions") or [],
        "recommendations": llm_result.get("recommendations") or [],
        "confidence": llm_result.get("confidence"),
        "sources": llm_result.get("sources") or [],
        "missing_information": llm_result.get("missing_information") or [],
    }

    try:
        if existing_answer is not None and force_refresh:
            # Archives the old version into AnswerHistoryCollection, then
            # overwrites the current one and bumps version.
            await answers_model.update_answer(error.id, answer_fields)
            persisted_answer = await answers_model.get_answer_by_error_id(error.id)

        else:
            persisted_answer = await answers_model.insert_answer(
                Answer(
                    error_id=error.id,
                    job_id=job.id if job is not None else None,
                    **answer_fields
                )
            )

        await job_model.update_status(
            error_message_id,
            status=JobProcessingEnums.ANSWERD.value
        )
    except Exception:
        logger.exception("Failed to persist answer for error_id=%s", error_id)
        return JSONResponse(
            status_code=status.HTTP_207_MULTI_STATUS,
            content={
                "result": ErrorEnums.LLM_ANSWER_FOUND.value,
                "llm_response": llm_result,
                "source": "llm",
                "warning": "failed_to_persist_answer",
            }
        )

    return JSONResponse(
        content={
            "result": ErrorEnums.LLM_ANSWER_FOUND.value,
            "llm_response": persisted_answer.model_dump(
             mode="json", by_alias=True, exclude_none=True
                        ),
            "source": "llm"
        }
    )