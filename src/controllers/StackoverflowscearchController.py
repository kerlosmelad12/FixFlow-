import httpx
import logging
from .BaseSearchController import BaseSearchController
from models.DB_Schema.Weabscearch import (
    WeabscearchQuestion,
    WeabscearchAnswers,
    WeabscearchResult,
    WeabscearchSearchResponse,
)
from models.Enums.Webscearchenums import Webscearchenums

logger = logging.getLogger(__name__)


class StackoverflowscearchController(BaseSearchController):

    def __init__(self):
        super().__init__()
        self.base_url = self.app_settings.STACK_OVERFLOW_BASE_URL

    async def get_question_scearch(self, client: httpx.AsyncClient, query: str, pagesize: int = 10):

        url = f"{self.base_url}/search/advanced"
        params = {
            "site": self.app_settings.STACK_OVERFLOW_SCEARCH_BACKEND,
            "q": query,
            "sort": "relevance",
            "order": "desc",
            "pagesize": pagesize,
            "filter": "withbody"
        }

        response = await client.get(url, params=params, timeout=10)
        response.raise_for_status()
        questions = response.json().get("items", [])

        return [
            WeabscearchQuestion(
                question_id=question["question_id"],
                title=question["title"],
                body=question.get("body", ""),
                tags=question.get("tags", []),
                url=question["link"],
                score=question.get("score", 0),
                answer_count=question.get("answer_count", 0)
            )
            for question in questions
        ]

    async def get_answers(self, client: httpx.AsyncClient, question_ids: list[int]):

        if not question_ids:
            return []

        ids = ";".join(map(str, question_ids))
        url = f"{self.base_url}/questions/{ids}/answers"
        params = {
            "site": self.app_settings.STACK_OVERFLOW_SCEARCH_BACKEND,
            "sort": "votes",
            "order": "desc",
            "filter": "withbody"
        }

        response = await client.get(url, params=params, timeout=10)
        response.raise_for_status()
        answers = response.json().get("items", [])

        return [
            WeabscearchAnswers(
                question_id=answer["question_id"],
                answer_id=answer["answer_id"],
                body=answer.get("body", ""),
                score=answer.get("score", 0),
                is_accepted=answer.get("is_accepted", False)
            )
            for answer in answers
        ]

    async def search(self, query: str, pagesize: int = 10):

        async with httpx.AsyncClient() as client:

            questions = await self.get_question_scearch(client, query=query, pagesize=pagesize)

            if not questions:
                return WeabscearchSearchResponse(results=[])

            question_ids = [q.question_id for q in questions]
            answers = await self.get_answers(client, question_ids)

        answers_by_question = {}
        for answer in answers:
            answers_by_question.setdefault(answer.question_id, []).append(answer)

        results = [
            WeabscearchResult(
                 source=Webscearchenums.STACK_OVERFLOW.value,
                question=question,
                answers=answers_by_question.get(question.question_id, [])
            )
            for question in questions
        ]

        return WeabscearchSearchResponse(results=results)