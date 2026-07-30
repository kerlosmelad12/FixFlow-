from abc import ABC,abstractmethod

class ClassifierInterface(ABC):

    @abstractmethod

    def load_model(self) :
        pass

    @abstractmethod
    def load_label_encoder(self):
        pass

    @abstractmethod
    def load_text_encoder(self):
        pass

    @abstractmethod
    def predict(self, test_data:str):
        pass
    