from enum import Enum

class JobProcessingEnums(Enum):
    PENDING = "pending"          
    EXTRACTED = "extracted"       
    SEARCHED = "searched"        
    FAILED = "failed"     
    ANSWERED = "ANSWERED"        