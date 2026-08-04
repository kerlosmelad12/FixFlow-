import os
from helper import get_settings


class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname(os.path.dirname(__file__))  # .../src
        self.database_dir = os.path.join(self.base_dir, "assests", "Database")
        self.models_dir = os.path.join(self.base_dir, "assests", "LLMModels")

        os.makedirs(self.database_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)

    def get_model_path(self, model_name: str = None) -> str:
        # HuggingFace's own models--org--name naming already namespaces
        # each model uniquely inside this shared cache folder.
        # Do NOT join model_name here — that caused nested/duplicate
        # cache paths and repeated re-downloads.
        return self.models_dir

    def get_database_path(self, db_name: str) -> str:
        database_path = os.path.join(self.database_dir, db_name)
        os.makedirs(database_path, exist_ok=True)
        return database_path
