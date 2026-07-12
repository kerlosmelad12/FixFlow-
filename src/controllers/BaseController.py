from helper import get_settings
from transformers import AutoModelForCausalLM

class BaseController:
    def __init__(self):
        self.app_settings=get_settings()
        



