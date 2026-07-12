from .BaseController import BaseController
from routes.schema.ErrorRequest import UserQueryRequest
class ProcessController(BaseController):
    def __init__(self):
        super().__init__()

    def Extract_error(self,error:UserQueryRequest):
        pass


