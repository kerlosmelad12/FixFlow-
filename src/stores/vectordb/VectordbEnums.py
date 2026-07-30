from enum import Enum
class VectordbEnums(Enum):
    QDRANT="qdrant"

class DistanceMetric(Enum):
    COSINE="cosine"
    DOT="dot"