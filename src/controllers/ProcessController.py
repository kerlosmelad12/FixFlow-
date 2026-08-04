from .BaseController import BaseController
import re
import html
import json

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

  
    