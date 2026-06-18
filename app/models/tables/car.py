from datetime import datetime, date
from sqlalchemy import Integer, String, Date, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM
from databases.postgresql import Base
from app.utils.energy_enum import CarEnum

class Car(Base):
    """
    Represents a car stored in the database.

    Attributes:
        id (int): The ID of the car stored in the database. Ex.: 1
        model (str): The model of the car stored in the database. Ex.: 'Zoe'
        registration (str): The registration of the car stored in the database. Ex.: 'AB-123-CD'
        first_registration_date (date): The first date of the car's registration stored in the database. Ex.: 2019-04-01
        energy (CarEnum): The energy of the car stored in the database. Ex.: 'diesel'
        color (str): The color of the car stored in the database. Ex.: 'red'
        brand_id (int): The ID of the brand stored in the database. Ex.: 5
        user_id (int): The ID of the user stored in the database. Ex.: 2
        created_at (datetime): The date when the car was created. Managed by the db. Ex.: 2019-04-01T12:00:00Z
        updated_at (datetime): The date when the car was last updated. Managed by the db. Ex.: 2020-04-01T12:00:00Z

    Relationships:
        user: User associated with the car.
        brand: Brand associated with the car.

    Notes:
        - The model must not exceed 50 characters.
        - The registration must not exceed 15 characters.
        - The color must not exceed 100 characters.
        - All user-provided fields are required.
    """

    __tablename__ = 'cars'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    model: Mapped[str] = mapped_column(String(50),nullable=False, index=True)
    registration: Mapped[str] = mapped_column(String(15), nullable=False)
    first_registration_date: Mapped[date] = mapped_column(Date, nullable=False)
    energy: Mapped[CarEnum] = mapped_column(ENUM(CarEnum, name="energy", create_type=False), nullable=False)
    color: Mapped[str] = mapped_column(String(100), nullable=False)
    brand_id: Mapped[int] = mapped_column(Integer, ForeignKey('brands.id'), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relation many-to-one with User entity
    user = relationship("User", back_populates="cars")
    # Relation many-to-one with Brand entity
    brand = relationship("Brand", back_populates="cars")
    # Relation one-to-many with Carpooling entity
    carpoolings = relationship("Carpooling", back_populates="car")