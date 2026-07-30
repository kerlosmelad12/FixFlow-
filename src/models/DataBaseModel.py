from helper.config import get_settings

class DataBaseModel:
    def __init__(self,db_client:object):
        self.app_setting=get_settings()
        self.db_client=db_client