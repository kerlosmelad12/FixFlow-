from ..ClassifierInterface import ClassifierInterface
import pickle as pk
import logging
import numpy as np


class ClusterProvider(ClassifierInterface):

    def __init__(
        self,
        model_path: str,
        encoder_path: str,
        text_encoder_path: str,
        confidence_threshold: float = -0.2,
        label_encoder_topk: int = 5,
    ):
        self.model_path = model_path
        self.encoder_path = encoder_path
        self.text_encoder_path = text_encoder_path

        self.confidence_threshold = confidence_threshold
        self.label_encoder_topk = label_encoder_topk

        self.classifier = None
        self.text_encoder = None
        self.label_encoder = None

        self.logger = logging.getLogger(__name__)

    def load_model(self):
        with open(self.model_path, "rb") as f:
            self.classifier = pk.load(f)

    def load_text_encoder(self):
        with open(self.text_encoder_path, "rb") as f:
            self.text_encoder = pk.load(f)

    def load_label_encoder(self):
        with open(self.encoder_path, "rb") as f:
            self.label_encoder = pk.load(f)


    def predict(self, text: str) -> dict[str, float]:

        if self.classifier is None:
                     self.logger.error("Classifier model is not loaded.")
        
        if self.text_encoder is None:
                    self.logger.error("Text encoder is not loaded.")
        
        if self.label_encoder is None:
                    self.logger.error("Label encoder is not loaded.")

        x = self.text_encoder.transform([text])

        scores = self.classifier.decision_function(x)[0]

        best_score = np.max(scores)

        if best_score < self.confidence_threshold:
            return {"Other": float(best_score)}

        topk_idx = np.argsort(scores)[::-1][: self.label_encoder_topk]

        results = {}

        for idx in topk_idx:
            label = self.label_encoder.inverse_transform([idx])[0]
            results[label] = float(scores[idx])

        return results