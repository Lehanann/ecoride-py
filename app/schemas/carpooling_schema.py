from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, time
from app.utils.carpooling_status_enum import CarpoolingStatusEnum

class CarpoolingBase(BaseModel):
    """
    Base schema for the carpooling, shared by create, update, and read operations and inherited by other schemas.

    Attributes:
        departure_date (date): The departure date.
        departure_time (time): The departure time.
        departure_location (str): The departure location.
        end_date (date): The end date.
        end_time (time): The end time.
        end_location (str): The end location.
        place_number (int): The number of available seats.
        price (Decimal): The price of the carpooling.
        car_id (int): The car used for the carpooling.

    Notes:
        - All fields defined in this schema are required.
        - departure_location and end_location must not exceed 200 characters.
    """
    departure_date: date = Field(..., description="The departure date.")
    departure_time: time = Field(..., description="The departure time.")
    departure_location: str = Field(..., max_length=200, description="The departure location.")
    end_date: date = Field(..., description="The end date.")
    end_time: time = Field(..., description="The end time.")
    end_location: str = Field(..., max_length=200, description="The end location.")
    place_number: int = Field(..., description="The number of available seats.")
    price: Decimal = Field(..., description="The price of the carpooling.")
    car_id: int = Field(..., description="The car used for the carpooling.")

class CarpoolingCreate(CarpoolingBase):
    """
    Schema used to create a new carpooling.

    Inherits all fields from Base schema.
    """
    pass

class CarpoolingUpdate(BaseModel):
    """
    Schema for updating an existing carpooling.

    All fields are optional. Only provided fields will be updated.

    Attributes:
        departure_date (date | None): The new departure date.
        departure_time (time | None): The new departure time.
        departure_location (str | None): The new departure location.
        end_date (date | None): The new end date.
        end_time (time | None): The new end time.
        end_location (str | None): The new end location.
        place_number (int | None): The number of available seats.
        price (Decimal | None): The price of the carpooling.
        car_id (int | None): The car used for the carpooling.

    Notes:
        - departure_location and end_location must not exceed 200 characters.
    """
    departure_date: date | None = Field(None, description="The new departure date.")
    departure_time: time | None = Field(None, description="The new departure time.")
    departure_location: str | None = Field(None, max_length=200, description="The new departure location.")
    end_date: date | None = Field(None, description="The new end date.")
    end_time: time | None = Field(None, description="The new end time.")
    end_location: str | None = Field(None, max_length=200, description="The new end location.")
    place_number: int | None = Field(None, description="The new number of available seats.")
    price: Decimal | None = Field(None, description="The new price of the carpooling.")
    car_id: int | None = Field(None, description="The new car used for the carpooling.")

class CarpoolingStatusUpdate(BaseModel):
    """
    Schema used to update only the status of a carpooling.

    Attributes:
        status: The new carpooling status.

    Notes:
        - Status is required.
    """
    status: CarpoolingStatusEnum = Field(..., description="The status of the carpooling.")

class CarpoolingRead(CarpoolingBase):
    """
    Schema used when reading an existing carpooling from the database.

    Inherits all fields from CarpoolingBase schema.

    Attributes:
        id (int): The ID of the carpooling.
        status (CarpoolingStatusEnum): The status of the carpooling.
    """
    id: int = Field(..., description="The ID of the carpooling.")
    status: CarpoolingStatusEnum = Field(..., description="The status of the carpooling.")

    model_config = ConfigDict(from_attributes=True)