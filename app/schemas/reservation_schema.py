from pydantic import BaseModel, Field

class ReservationCreate(BaseModel):
    """
    Schema used to create a new reservation.

    Attributes:
        carpooling_id (int): The Identifier of carpooling

    Notes:
        - The carpooling_id is required.
    """
    carpooling_id: int = Field(..., description="The id of the carpooling that this reservation belongs to")

