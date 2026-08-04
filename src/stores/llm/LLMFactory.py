from .LLMEnums import LLMbackend
from .providers.QweenProvider import QweenProvider
from .providers.SentenceProvider import SentenceProvider
from .providers.GroqProvider import GroqProvider

class LLMFactory:

    def __init__(self, config: dict):
        self.config = config

    def create(self, provider: str):
        if provider == LLMbackend.EMBEDDING_BACKEND.value:
            return SentenceProvider(self.config.EMBEDDING_MODEL_NAME)

        if provider == LLMbackend.GENERATION_BACKEND.value:
            return GroqProvider(
                api_key=self.config.GROQ_API_KEY,
                model_name=self.config.GROQ_MODEL_NAME,
            )

        raise ValueError(f"Unsupported LLM provider: {provider!r}")