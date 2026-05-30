from pydantic import BaseModel, Field
from datetime import date
from app.utils.energy_enum import CarEnum


class CarBase(BaseModel):
    """
    Base schema for the car, shared by create, update, and read operations and inherited by other schemas.

    Attributes:
        model (str): The model of the car.
        registration (str): The registration of the car.
        first_registration_date (date): The first date of the car registration.
        energy (CarEnergy): The energy of the car.
        color (str): The color of the car.
        brand_id (int): The brand ID of the car.
    """
    model: str = Field(..., description="The model of the car.")
    registration: str = Field(..., description="The registration of the car.")
    first_registration_date: date = Field(..., description="The first date registration of the car.")
    energy: CarEnum = Field(..., description="The energy of the car.")
    color: str = Field(..., description="The color of the car.")
    brand_id: int = Field(..., description="The brand ID of the car.")

class CarCreate(CarBase):
    """
    Schema used when creating a new car.

    Inherits all fields from CarBase schema.
    """
    pass

class CarRead(CarBase):
    """
    Schema used when reading an existing car from the database.

    Inherits all fields from CarBase schema.

    Attributes:
        id (int): The ID of the car.
    """
    id : int = Field(..., description="The id of the car.")