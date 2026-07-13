from .BaseController import BaseController
from models import ErrorEnums
from models.DB_Schema.ErrorMessage import ErrorMessage
import re
import hashlib
class DataController(BaseController):
    def __init__(self):
        super().__init__()

    def validate_error(self, error: str):
        if error.strip() == "": 
           return False, ErrorEnums.NOT_APPROVED_SIZE.value

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
    
    @classmethod
    def generate_error_id(error_title: str, cleaned_text: str) -> str:
      slug = re.sub(r'[^a-z0-9]+', '-', error_title.lower()).strip('-')
      slug = slug[:40]    
  
      short_hash = hashlib.sha256(cleaned_text.strip().lower().encode()).hexdigest()[:6]
    
      return f"{slug}-{short_hash}"
    
       
    
    

           
           
       
    

    

    