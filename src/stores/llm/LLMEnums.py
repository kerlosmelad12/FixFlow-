from enum import Enum
import torch
class LLMbackend(Enum):
    EMBEDDING_BACKEND="MiniLM"
    GENERATION_BACKEND = "Groq"


class Devicemap(Enum):
    CUDA="cuda"
    CPU="cpu"
    AUTO="auto"


class TorchDType(Enum):
    FLOAT32 = torch.float32
    FLOAT16 = torch.float16
    BFLOAT16 = torch.bfloat16
    FLOAT64 = torch.float64
    INT8 = torch.int8
    INT16 = torch.int16
    INT32 = torch.int32
    INT64 = torch.int64
    BOOL = torch.bool

class ChatRoles(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
