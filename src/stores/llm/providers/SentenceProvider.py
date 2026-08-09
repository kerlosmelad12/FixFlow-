from ..LLMInterface import LLMInterface
import torch
import logging
from sentence_transformers import SentenceTransformer


class SentenceProvider(LLMInterface):

    def __init__(self, model_name, input_defualt_max_characters: int = 1024):
        self.model_name = model_name
        self.tokenizer = SentenceTransformer(self.model_name)
        self.input_defualt_max_characters = input_defualt_max_characters
        self.embedding_size = self.tokenizer.get_sentence_embedding_dimension()
        self.logger = logging.getLogger(__name__)

    def set_generation_model(self, model_id: str):
        raise NotImplementedError("this model not supported in generation")

    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.model_name = model_id
        self.embedding_size = embedding_size
        self.tokenizer = SentenceTransformer(self.model_name)

    def construct_prompt(self, role: str, message: str):
        raise NotImplementedError("this function not supported in LocalEmbedding Provider")

    

    def generate (self,promot: str,messages: list[dict] | dict,max_new_tokens: int = None, temperature: float = None) -> str:

        raise NotImplementedError("this function not supported in LocalEmbedding Provider")

    

    def process_text(self, text: str):
        return text[0:self.input_defualt_max_characters].strip()

    

    def  embed(self, text) -> list[list[float]]:

        if self.tokenizer is None:
            self.logger.error("local embedding model not loaded")
            return None

        is_batch = isinstance(text, list)
        texts = text if is_batch else [text]
        texts = [self.process_text(t) for t in texts]

        try:
            embeddings = self.tokenizer.encode(texts, convert_to_numpy=True  , batch_size=64)
        except Exception as e:
            self.logger.error(f"Error while embedding text locally: {e}")
            return None

        embeddings = [vec[: self.embedding_size].tolist() for vec in embeddings]

        return embeddings if is_batch else embeddings[0]