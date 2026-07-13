from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    
    QUESTION_MIN_LENGTH: int
    QUESTION_MAX_LENGTH: int
    ERROR_KEYWORDS: str
    
    DB_NAME: str
    MONGODB_URI: str
    
    
    LLM_DATA_EXTRACTOR_PATH: str
    MODELS_CACHE_PATH: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"  # يتجاهل أي متغيرات إضافية في .env مش معرّفة هنا
    )


    def get_error_keywords(self):
      return [kw.strip() for kw in self.ERROR_KEYWORDS.split(",")]
 


def get_settings():
    return Settings()




