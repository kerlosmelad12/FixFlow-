from .LLMEnums import LLMbackend
from .providers.QweenProvider import QweenProvider
from .providers.SentenceProvider import SentenceProvider

class LLMFactory:

    def __init__(self,config:dict):
        self.config=config


    def create(self,provider:str):
        if provider == LLMbackend.EMBEDDING_BACKEND.value:
            return SentenceProvider(self.config.EMBEDDING_MODEL_NAME)

        if provider == LLMbackend.GENERATION_BACKEND.value:
            return QweenProvider(model_name=self.config.LLM_DATA_EXTRACTOR_NAME)

        