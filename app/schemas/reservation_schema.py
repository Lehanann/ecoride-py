from pydantic import BaseModel, Field

class ReservationCreate(BaseModel):
    """
    Schema used to create a new reservation.

    Attributes:
        carpooling_id (int): The unique identifier of carpooling
    """
    carpooling_id: int = Field(..., description="The id of the carpooling to reserve.")

