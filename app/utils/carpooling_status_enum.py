from enum import Enum

class CarpoolingStatusEnum(str, Enum):
    draft = 'draft'
    published = 'published'
    finished = 'finished'
    cancelled = 'cancelled'
