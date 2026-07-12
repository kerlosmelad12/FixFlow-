from enum import Enum

class TagStatus(str, Enum):
    APPROVED = "approved"   
    PENDING = "pending"        
    MERGED = "merged"           
    REJECTED = "rejected"      
