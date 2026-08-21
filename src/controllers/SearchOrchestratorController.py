import asyncio
import logging
from .BaseController import BaseController
from .GithubSearchController import GithubSearchController
from .StackoverflowscearchController import StackoverflowscearchController
from models.DB_Schema.Weabscearch import WeabscearchSearchResponse
from models.Enums.Webscearchenums import Webscearchenums

logger = logging.getLogger(__name__)

_BACKEND_TO_CONTROLLER = {
    Webscearchenums.GITHUB.value: GithubSearchController,
    Webscearchenums.STACK_OVERFLOW.value: StackoverflowscearchController,
}


class SearchOrchestratorController(BaseController):

    async def search_all_sources(
        self, query: str, pagesize: int, limit: int
    ) -> WeabscearchSearchResponse:

        scearch_backend = self.app_settings.get_all_scearch_backends()

        controllers = [
            _BACKEND_TO_CONTROLLER[backend]()
            for backend in scearch_backend
            if backend in _BACKEND_TO_CONTROLLER
        ]

        results_per_source = await asyncio.gather(
            *[controller.search(query, pagesize) for controller in controllers],
            return_exceptions=True
        )

        combined = []
        for controller, source_result in zip(controllers, results_per_source):

            if isinstance(source_result, Exception):
                logger.warning(
                    "Search source %s failed: %s",
                    type(controller).__name__,
                    source_result
                )
                continue

            combined.extend(source_result.results)

        return WeabscearchSearchResponse(results=combined[:limit])