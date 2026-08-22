from .BaseController import BaseController
from models import ErrorEnums
from models.DB_Schema.ErrorMessage import ErrorMessage
import re
import hashlib


class DataController(BaseController):
    def __init__(self):
        super().__init__()

    def validate_error(self, error: str):
        stripped = error.strip()

        if stripped == "":
            return False, ErrorEnums.NOT_APPROVED_SIZE.value

        if len(error) < self.app_settings.QUESTION_MIN_LENGTH:
            return False, ErrorEnums.NOT_APPROVED_SIZE.value

        if len(error) > self.app_settings.QUESTION_MAX_LENGTH:
            return False, ErrorEnums.NOT_APPROVED_SIZE.value

        return True, ErrorEnums.ERROR_VALIDATED.value

    @classmethod
    def generate_error_id(cls, cleaned_text: str) -> str:
        normalized = re.sub(r"\s+", " ", cleaned_text.strip().lower())

        return hashlib.sha256(normalized.encode()).hexdigest()