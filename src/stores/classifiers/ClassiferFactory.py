from .providers.ClusterProvider import ClusterProvider
from .ClassificationEnums import ClassificationEnums

class ClassiferFactory:
    def __init__(self,config:dict):
        self.config=config


    def create(self,provider):
        if provider== ClassificationEnums.CLASSIFICATION.value:
            
            return ClusterProvider(model_path=self.config.CLASSIFIER_MODEL_PATH,encoder_path=self.config.LABEL_ENCODER_PATH,
                                   text_encoder_path=self.config.TFIDF_MODEL_PATH)

        
        