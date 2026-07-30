
class NlpController:
    def __init__(self, embedding_client: object,generation_client: object,
                 vector_store_client: object,classifier_client: object):
        super().__init__()
        self.embedding_client = embedding_client
        self.generation_client = generation_client
        self.vector_store_client = vector_store_client
        self.classifier_client = classifier_client



    def classify_text(self, text: str):

        result=self.classifier_client.predict(text)
        if result is None:
            return None
        return result
            
        


        


