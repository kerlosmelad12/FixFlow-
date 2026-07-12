from .BaseController import BaseController
from routes.schema.ErrorRequest import UserQueryRequest
from .LLMController import LLMService
from .DataController import DataController
from models.DB_Schema.ProcessingJob import ProcessingJob
from models.Enums.JobProcessingEnums import JobProcessinEnums
import re
import html
from prompts.extraction_prompts import build_extraction_prompt


class ProcessController(BaseController):
    def __init__(self):
        super().__init__()
        self.model = LLMService.get_langchain_pipeline()
        self.data_controller = DataController()

    def validate(self, user_request: UserQueryRequest):
        return self.data_controller.validate_error(user_request.query)

    def create_job(self, user_request: UserQueryRequest):
        return ProcessingJob(
            error=user_request.query,
            status=JobProcessinEnums.PENDING.value
        )

    def clean_text(self, error_text: str) :
        text = error_text.lower()
        text = re.sub(r'<[^>]+>', ' ', text)
        text = html.unescape(text)
        text = re.sub(r'\b[a-z0-9]{20,}\b', '<ID>', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_error(self, cleaned_text: str):
        extracted_raw=self.model.invoke(build_extraction_prompt(cleaned_text))
        return extracted_raw

    def process_new_error(self, user_request: UserQueryRequest):
        is_valid, signal = self.validate(user_request)
        if not is_valid:
            return {"success": False, "message": signal}

        job = self.create_job(user_request)
    
        cleaned_text = self.clean_text(user_request.query)
    
        extracted = self.extract_error(cleaned_text)   # ← السطر ده لازم يكون موجود قبل الـ return

        return {"extracted": extracted, "cleaned_text": cleaned_text, "job_id": job.job_id, "status": job.status}