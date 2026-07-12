from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    #Application Settings 
    APP_NAME: str
    APP_VERSION: str

    # Question Variables
    ERROR_KEYWORDS: str
    QUESTION_MAX_LENGTH:int
    QUESTION_MIN_LENGTH:int


    #Database Configuration
    DB_NAME:str
    MONGODB_URI:str



    def get_error_keywords(self):
      return [kw.strip() for kw in self.ERROR_KEYWORDS.split(",")]
 

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()




