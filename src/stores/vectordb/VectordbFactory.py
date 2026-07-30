from .VectordbEnums import VectordbEnums
from .providers.QDrantProvider import QDrantProvider
from controllers import BaseController


class VectordbFactory:
    def __init__(self,config):
        self.base_controller=BaseController()
        self.config=config

    def create(self,provider:str):

        if provider==self.config.VECTOR_STORE_BACKEND:
            return QDrantProvider(db_path=self.base_controller.get_database_path(VectordbEnums.QDRANT.value))
        
