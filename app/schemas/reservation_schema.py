from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict
from datetime import date, time

class ReservationCreate(BaseModel):
    """
    Schema used to create a new reservation.

    Attributes:
        carpooling_id (int): The unique identifier of carpooling
    """
    carpooling_id: int = Field(..., description="The id of the carpooling to reserve.")

class UserSummary(BaseModel):
    id: int = Field(..., description="The id of the driver.")
    username: str = Field(..., description="The username of the driver.")

    model_config = ConfigDict(from_attributes=True)

class CarSummary(BaseModel):
    model: str
    registration: str

    user: UserSummary

    model_config = ConfigDict(from_attributes=True)

class CarpoolingSummary(BaseModel):
    id: int = Field(..., description="The unique identifier of carpooling to reserve.")
    departure_date: date = Field(..., description="The departure date of the carpooling.")
    departure_time: time = Field(..., description="The departure time of the carpooling.")
    departure_location: str = Field(..., description="The departure location of the carpooling.")
    end_location: str = Field(..., description="The destination location of the carpooling.")
    price: Decimal = Field(..., description="The price of the reservation.")

    car: CarSummary

    model_config = ConfigDict(from_attributes=True)

class UserReservationResponse(BaseModel):
    carpooling: CarpoolingSummary

    model_config = ConfigDict(from_attributes=True)