from ..LLMInterface import LLMInterface
from groq import Groq
import logging
from ..LLMEnums import ChatRoles


class GroqProvider(LLMInterface):

    def __init__(self, api_key: str, model_name: str,
                 default_TEMPERATURE: float = 0.2,
                 MAX_OUTPUT_TOKENS: int = 2048,
                 INPUT_MAX_CHRACTERS: int = 100000000):

        self.client = Groq(api_key=api_key)
        self.model_name = model_name
        self.default_TEMPERATURE = default_TEMPERATURE
        self.max_output_tokens = MAX_OUTPUT_TOKENS
        self.input_max_chracters = INPUT_MAX_CHRACTERS
        self.logger = logging.getLogger(__name__)
        self.enums = ChatRoles

    def set_generation_model(self, model_id: str):
        self.model_name = model_id

    def set_embedding_model(self, model_id, embedding_size):
        raise NotImplementedError("Groq provider does not support embeddings")

    def generate(self, promot: str, messages: list[dict] | dict,
                 max_new_tokens: int = None, temperature: float = None,
                 json_mode: bool = False):
    
        

        if isinstance(messages, dict):
            messages = [messages]

        if promot:
            messages = [
                self.construct_prompt(ChatRoles.USER.value, promot),
                *messages
            ]

        kwargs = dict(
            model=self.model_name,
            messages=messages,
            max_tokens=max_new_tokens or self.max_output_tokens,
            temperature=temperature if temperature is not None else self.default_TEMPERATURE,
        )

        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        response = self.client.chat.completions.create(**kwargs)

        return response.choices[0].message.content

    def embed(self, text) -> list[list[float]]:
        raise NotImplementedError("this model not support for embedding data")

    def construct_prompt(self, role: str, message: str):
        return {'role': role, 'content': message}

    def process_text(self, text: str):
        return text[0:self.input_max_chracters].strip()