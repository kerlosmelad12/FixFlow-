import os
from helper import get_settings


class BaseController:
    def __init__(self):
        self.app_settings = get_settings()

        self.base_dir = os.path.dirname(os.path.dirname(__file__))

        self.database_dir = os.path.join(
            self.base_dir,
            "assests",
            "Database"
        )

        self.models_dir = os.path.join(
            self.base_dir,
            "assests",
            "LLMModels"
        )

    def get_model_path(self, model_name: str):
        model_path = os.path.join(
            self.models_dir,
            model_name
        )

        os.makedirs(model_path, exist_ok=True)

        return model_path

    def get_database_path(self, db_name: str):
    
        database_path = os.path.join(
                self.database_dir, db_name
            )
    
        if not os.path.exists(database_path):
                os.makedirs(database_path)
    
        return database_path