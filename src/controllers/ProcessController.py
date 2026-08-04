from .BaseController import BaseController
from routes.schema.ErrorRequest import UserQueryRequest
from models.DB_Schema.ProcessingJob import ProcessingJob
from models.Enums.JobProcessingEnums import JobProcessingEnums
import re
import html
from prompts.extraction_prompts import build_user_prompt,build_system_prompt
import json
from .extraction_parsing import parse_extraction_output

class ProcessController(BaseController):
    def __init__(self):
        super().__init__()

    def clean_text(self, error_text: str) :
        text = error_text.lower()
        text = re.sub(r'<[^>]+>', ' ', text)
        text = html.unescape(text)
        text = re.sub(r'\b[a-z0-9]{20,}\b', '<ID>', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_error_data(self, cleaned_text: str,llm_model:object):
        extracted_raw=llm_model.invoke(build_extraction_prompt(cleaned_text))
        result=parse_extraction_output(extracted_raw)
        if not result["success"]:
           return {"error": result["error"]} 

        return result
    