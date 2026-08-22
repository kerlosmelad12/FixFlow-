from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str
    APP_VERSION: str

    # Question validation
    QUESTION_MIN_LENGTH: int = Field(gt=0)
    QUESTION_MAX_LENGTH: int = Field(gt=0)

    # Database
    DB_NAME: str
    MONGODB_URI: str 

    # LLM Configuration
    LLM_PROVIDER: Literal["local_transformers", "openai_compatible"] = "local_transformers"
    LLM_DATA_EXTRACTOR_NAME: str
    MODEL_DIR: str
    MAX_OUTPUT_TOKENS: int = Field(gt=0, default=2048)
    TEMPERATURE: float = Field(ge=0.0, le=2.0, default=0.7)
    DEVICE: Literal["cpu", "cuda", "auto"] = "cpu"
    TORCH_DTYPE: Literal["float16", "bfloat16", "float32"] = "float16"
    LOAD_IN_4BIT: bool = False
    LLM_API_KEY: SecretStr = SecretStr("")
    LLM_API_BASE_URL: str = ""
    GROQ_API_KEY: str
    GROQ_MODEL_NAME: str

    # Embedding
    EMBEDDING_MODEL_NAME: str
    EMBEDDING_DEVICE: Literal["cpu", "cuda", "auto"] = "cpu"
    EMBEDDING_BATCH_SIZE: int = Field(gt=0, default=32)
    INPUT_MAX_CHRACTERS:int
    EMBEDDING_SIZE:int
    EMBEDDING_BACKEND:str
    GENERATION_BACKEND:str

    # TF-IDF

    TFIDF_MODEL_PATH: Path

    # Classifier
    CLASSIFIER_MODEL_PATH: Path
    CLUSTER_CONFIDENCE_THRESHOLD: float = Field(ge=0.0, le=1.0, default=0.6)
    CLASSIFIER_BACKEND:str

    # Encoder
    LABEL_ENCODER_PATH:Path
    LABEL_ENCODER_FALLBACK_LABEL:str
    LABEL_ENCODER_TOP_K:int

    DISTANCE_METRIC:str
    DATABASE_FOLDER:str
    VECTOR_STORE_BACKEND:str

    # Language Configuration
    DEFAULT_LANGUAGE:str
    PRIMARY_LANGUAGE:str

    ##search Configuration
    STACK_OVERFLOW_SCEARCH_BACKEND:str
    GITHUB_SCEARCH_BACKEND:str
    STACK_OVERFLOW_BASE_URL:str
    GITHUB_TOKEN:str
    GITHUB_BASE_URL:str

    MAX_ANSWER_CHARS:int
    MAX_QUESTION_CHARS:int
    MAX_ANSWERS_PER_DOCUMENT:int
    MAX_DOCUMENTS:int

    CACHE_TTL_SECONDS:int
    REDIS_URL:str

    DEDUP_SIMILARITY_THRESHOLD:float

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    
    def get_all_scearch_backends(self) -> list[str]:
        return [
            self.STACK_OVERFLOW_SCEARCH_BACKEND,
            self.GITHUB_SCEARCH_BACKEND,
        ]





def get_settings() -> Settings:
    return Settings()