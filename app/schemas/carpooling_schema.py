from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from datetime import date, time
from app.utils.carpooling_status_enum import CarpoolingStatusEnum

class CarpoolingBase(BaseModel):
    """
    Base schema for the carpooling, shared by create, update, and read operations and inherited by other schemas.
    Attributes:
        departure_date (date): The departure date of the carpooling.
        departure_time (time): The departure time of the carpooling.
        departure_location (str): The departure location of the carpooling.
        end_date (date): The end date of the carpooling.
        end_time (time): The end time of the carpooling.
        end_location  (str): The end location of the carpooling.
        place_number (int): The place number of the carpooling.
        price (Decimal): The price of the carpooling.
        car_id (int): The ID of the car used for the carpooling.

    Notes:
        - All fields are required.
        - departure_location and end_location must not exceed 200 characters.
    """
    departure_date: date = Field(..., description="The departure date of the carpooling.")
    departure_time: time = Field(..., description="The departure time of the carpooling.")
    departure_location: str = Field(...,max_length=200, description="The departure location of the carpooling.")
    end_date: date = Field(..., description="The end date of the carpooling.")
    end_time: time = Field(..., description="The end time of the carpooling.")
    end_location: str = Field(...,max_length=200, description="The end location of the carpooling.")
    place_number: int = Field(..., description="The place number of the carpooling.")
    price: Decimal = Field(..., description="The price of the carpooling.")
    car_id: int = Field(..., description="The ID of the carpooling.")

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
        departure_date (date | None): The new departure date of the carpooling.
        departure_time (time | None): The new departure time of the carpooling.
        departure_location (str | None): The new departure location of the carpooling.
        end_date (date | None): The new end date of the carpooling.
        end_time (time | None): The new end time of the carpooling.
        end_location (str | None): The new end location of the carpooling.
        place_number (int): The place number of the carpooling.
        price (Decimal): The price of the carpooling.
        car_id (int): The ID of the car used the carpooling.

    Notes:
        - departure_location and end_location must not exceed 200 characters.
    """
    departure_date: date | None = Field(None, description="The new departure date of the carpooling.")
    departure_time: time | None = Field(None, description="The new departure time of the carpooling.")
    departure_location: str | None = Field(None, max_length=200, description="The new departure location of the carpooling.")
    end_date: date | None = Field(None, description="The new end date of the carpooling.")
    end_time: time | None = Field(None, description="The new end time of the carpooling.")
    end_location: str | None = Field(None, max_length=200, description="The new end location of the carpooling.")
    place_number: int | None = Field(None, description="The place number of the carpooling.")
    price: Decimal | None = Field(None, description="The price of the carpooling.")
    car_id: int | None = Field(None, description="The ID of the carpooling.")

class CarpoolingStatusUpdate(BaseModel):
    """
    Schema for updating an existing status carpooling only.

    Notes:
        - Status is required.
    """
    status: CarpoolingStatusEnum = Field(..., description="The status of the carpooling.")

class CarpoolingRead(CarpoolingBase):
    """
    Schema used when reading an existing carpooling from the database.

    Inherits all fields from CarpoolingBase schema.

    Attributes:
        id (int): The id of the carpooling.
        status (CarpoolingStatusEnum): The status of the carpooling.
    """
    id: int = Field(..., description="The ID of the carpooling.")
    status: CarpoolingStatusEnum = Field(..., description="The status of the carpooling.")

    model_config = ConfigDict(from_attributes=True)