from .BaseController import BaseController
from models import ErrorEnums
class DataController(BaseController):
    def __init__(self):
        super().__init__()

    def validate_error(self, error: str):
        if len(error) < self.app_settings.QUESTION_MIN_LENGTH:
          return False, ErrorEnums.NOT_APPROVED_SIZE.value

        if len(error) > self.app_settings.QUESTION_MAX_LENGTH:
           return False, ErrorEnums.NOT_APPROVED_SIZE.value

        if error.strip() == "":
          return False, ErrorEnums.NOT_APPROVED_SIZE.value

        keywords = self.app_settings.get_error_keywords()
        lowered = error.lower()
        if not any(keyword.lower() in lowered for keyword in keywords):
          return False, ErrorEnums.ERROR_CONTANT_NOT_APPROVED.value

        return True, ErrorEnums.ERROR_VALIDATED.value