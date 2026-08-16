import httpx
import asyncio
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


class GithubSearchController(BaseSearchController):

    def __init__(self):
        super().__init__()
        self.base_url = self.app_settings.GITHUB_BASE_URL
        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.app_settings.GITHUB_TOKEN}",
        }

    async def _search_issues(self, client: httpx.AsyncClient, query: str, pagesize: int):
        url = f"{self.base_url}/search/issues"
        params = {
            "q": f"{query} is:issue is:closed in:title,body",
            "sort": "relevance",
            "order": "desc",
            "per_page": pagesize,
        }
        response = await client.get(url, params=params, timeout=10)
        response.raise_for_status()
        return [
            issue for issue in response.json().get("items", [])
            if "pull_request" not in issue
        ]

    async def _get_comments_for_issue(self, client: httpx.AsyncClient, issue: dict):
        try:
            response = await client.get(
                issue["comments_url"],
                params={"per_page": self.app_settings.MAX_ANSWERS_PER_DOCUMENT},
                timeout=10
            )
            response.raise_for_status()
        except Exception:
            logger.exception(
                "GithubSearchController: failed fetching comments for issue %s",
                issue.get("number")
            )
            return []

        comments = response.json()

        return [
            WeabscearchAnswers(
                question_id=issue["number"],
                answer_id=comment["id"],
                body=comment.get("body", ""),
                score=comment.get("reactions", {}).get("total_count", 0),
                is_accepted=(
                    comment.get("author_association") in ("OWNER", "MEMBER", "COLLABORATOR")
                )
            )
            for comment in comments
        ]

    async def search(self, query: str, pagesize: int = 10):

        async with httpx.AsyncClient(headers=self.headers) as client:

            raw_issues = await self._search_issues(client, query, pagesize)

            if not raw_issues:
                return WeabscearchSearchResponse(results=[])

            comment_lists = await asyncio.gather(
                *[self._get_comments_for_issue(client, issue) for issue in raw_issues]
            )

        questions = [
            WeabscearchQuestion(
                question_id=issue["number"],
                title=issue["title"],
                body=issue.get("body") or "",
                tags=[label["name"] for label in issue.get("labels", [])],
                url=issue["html_url"],
                score=issue.get("reactions", {}).get("total_count", 0),
                answer_count=issue.get("comments", 0)
            )
            for issue in raw_issues
        ]

        answers_by_question = {}
        for comments in comment_lists:
            for answer in comments:
                answers_by_question.setdefault(answer.question_id, []).append(answer)

        results = [
            WeabscearchResult(
                source=Webscearchenums.GITHUB.value,
                question=question,
                answers=answers_by_question.get(question.question_id, [])
            )
            for question in questions
        ]

        return WeabscearchSearchResponse(results=results)