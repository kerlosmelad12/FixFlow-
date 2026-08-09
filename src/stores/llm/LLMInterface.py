from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional




class LLMInterface(ABC):

    @abstractmethod
    def generate(self,promot: str,messages: list=None | dict,max_new_tokens: int = None, temperature: float = None) -> str:
        pass

    @abstractmethod
    def embed(self, text) -> list[list[float]]:
        pass

    @abstractmethod
    def set_generation_model(self, model_id: str):
        pass


    @abstractmethod
    def set_embedding_model(self, model_id: str, embedding_size: int):
        pass



    @abstractmethod
    def construct_prompt(self, role: str, message: str) :
        return {'role':role,
                'content':message}
       
        