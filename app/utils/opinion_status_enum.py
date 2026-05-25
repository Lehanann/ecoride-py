from enum import Enum

class OpinionStatusEnum(str, Enum):
    pending = 'pending'
    approved = 'approved'
    rejected = 'rejected'