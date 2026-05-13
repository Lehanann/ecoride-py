from sqlalchemy import Integer, String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM
from datetime import date
from databases.postgresql import Base
from app.utils.energy_enum import CarEnum

class Car(Base):
    """
    Represents a car stored in the database.
    Attributes:
        id (int): The ID of the car stored in the database.
        model (str): The model of the car stored in the database.
        registration (str): The registration of the car stored in the database.
        first_date_registration (date): The first date of the car's registration stored in the database.
        energy (CarEnum): The energy of the car stored in the database.
        color (str): The color of the car stored in the database.
        brand_id (int): The ID of the brand stored in the database.
        user_id (int): The ID of the user stored in the database.
    Notes:
        - The model must not exceed 50 characters.
        - The model is required.
    """

    __tablename__ = 'cars'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    model: Mapped[str] = mapped_column(String(50),nullable=False, index=True)
    registration: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    first_date_registration: Mapped[date] = mapped_column(Date, nullable=False)
    energy: Mapped[CarEnum] = mapped_column(ENUM(CarEnum, name="car_enum", create_type=False), nullable=False)
    color: Mapped[str] = mapped_column(String(100), nullable=False)
    brand_id: Mapped[int] = mapped_column(Integer, ForeignKey('brands.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)

    user = relationship("User", back_populates="cars")
    brand = relationship("Brand", back_populates="cars")

    carpoolings = relationship("Carpooling", back_populates="car")