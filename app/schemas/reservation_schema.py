from pydantic import BaseModel, Field

class ReservationCreate(BaseModel):

    carpooling_id: int = Field(..., description="The id of the carpooling that this reservation belongs to")

