from .BaseController import BaseController
import requests
import logging
from models.DB_Schema.Weabscearch import WeabscearchQuestion,WeabscearchAnswers,WeabscearchResult,WeabscearchSearchResponse

class WebscearchController(BaseController):
    def __init__(self, scearch_backend: str, similer_question_result: int = 10):
        super().__init__()
        self.similer_question_result = similer_question_result
       
        if scearch_backend == self.app_settings.STACK_OVERFLOW_SCEARCH_BACKEND:
            self.base_url = self.app_settings.STACK_OVERFLOW_BASE_URL
        else:
            self.base_url = None

    def get_question_scearch(self,query: str,pagesize: int = 10):

        url = f"{self.base_url}/search/advanced"

        params = {
            "site": self.app_settings.STACK_OVERFLOW_SCEARCH_BACKEND,
            "q": query,
            "sort": "relevance",
            "order": "desc",
            "pagesize": pagesize,
            "filter": "withbody"
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

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

    def get_answers (self, question_ids: list[int]):

        if not question_ids:
            return []

        ids = ";".join(
            map(str, question_ids)
        )

        url = f"{self.base_url}/questions/{ids}/answers"

        params = {
            "site": self.app_settings.STACK_OVERFLOW_SCEARCH_BACKEND,
            "sort": "votes",
            "order": "desc",
            "filter": "withbody"
        }

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        response.raise_for_status()

        answers = response.json().get("items", [])

        return [
            WeabscearchAnswers(
                question_id=answer["question_id"],
                answer_id=answer["answer_id"],
                body=answer.get("body", ""),
                score=answer.get("score", 0),
                is_accepted=answer.get(
                    "is_accepted",
                    False
                )
            )
            for answer in answers
        ]
    def search( self, query: str , pagesize: int = 10):

        questions = self.get_question_scearch(
            query=query,
            pagesize=pagesize
        )

        if not questions:
            return WeabscearchSearchResponse(
                results=[]
            )

        question_ids = [
            question.question_id
            for question in questions
        ]

        answers = self.get_answers(
            question_ids
        )

        answers_by_question = {}

        for answer in answers:

            question_id = answer.question_id

            if question_id not in answers_by_question:
                answers_by_question[question_id] = []

            answers_by_question[question_id].append(
                answer
            )

        results = []

        for question in questions:

            results.append(
                WeabscearchResult(
                    source="stackoverflow",
                    question=question,
                    answers=answers_by_question.get(
                        question.question_id,
                        []
                    )
                )
            )

        return WeabscearchSearchResponse(
            results=results
        )