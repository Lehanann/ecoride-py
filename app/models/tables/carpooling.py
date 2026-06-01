from sqlalchemy import Integer, String, Date, Time, ForeignKey, Numeric, text, DateTime, func, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from databases.postgresql import Base
from datetime import date, time, datetime
from sqlalchemy.dialects.postgresql import ENUM
from app.utils.carpooling_status_enum import CarpoolingStatusEnum
from decimal import Decimal

class Carpooling(Base):
    """
    Represents a carpooling stored in the database.

    Attributes:
        id (int): The ID of the carpooling. Ex.: 1
        departure_date (date): The departure date. Ex.: '2020-04-01' YYYY-MM-DD
        departure_time (time): The departure time. Ex.: '07:00'
        departure_location (str): The departure location. Ex.: '15 av. Mystery 69999 Les-Orchidés'
        end_date (date): The end date. Ex.: '2020-04-01' YYYY-MM-DD
        end_time (time): The end time. Ex.: '07:40'
        end_location (str): The end location. Ex.: '39 Bis impasse des Secrets 69899 Le Bois-Enchanté'
        status (CarpoolingStatusEnum): The status of the carpooling initialized to draft by the db. Ex.: 'draft'
        place_number (int): Number of available seats. Ex.: 2
        price (Decimal): The price of the carpooling. Ex.: 4
        car_id (int): The ID of the car used for the carpooling. Ex.: 12
        created_at (datetime): The date when the carpooling was created. Managed by the db. Ex.: 2019-04-01T12:00:00Z
        updated_at (datetime): The date when the carpooling was last updated. Managed by the db. Ex.: 2020-04-01T12:00:00Z

    Relationships:
        car: The car associated with the carpooling.
        reservations: Reservations associated with the carpooling.
        opinions: The opinions associated with the carpooling.

    Notes:
        - All user-provided fields are required.
        - departure_location and end_location must not exceed 200 characters.
        - The price must be greater than 2 credits.
        - The maximum value depends on the database constraint (Numeric(6,2)).
    """
    __tablename__ = "carpoolings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    departure_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    departure_time: Mapped[time] = mapped_column(Time, nullable=False, index=True)
    departure_location: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_location: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[CarpoolingStatusEnum] = mapped_column(ENUM(CarpoolingStatusEnum,
                                                              name="carpooling_status",
                                                              create_type=False),
                                                         nullable=False,
                                                         server_default=text("'draft'"))
    place_number: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    car_id: Mapped[int] = mapped_column(Integer, ForeignKey('cars.id'), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relation many-to-one with Car entity
    car = relationship("Car", back_populates="carpoolings")
    # Relation one-to-many with Reservation entity
    reservations = relationship("Reservation", back_populates="carpooling")
    # Relation one-to-many with opinion Entity
    opinions = relationship("Opinion", back_populates="carpooling")
    # Relation one-to-many with Transaction entity
    transactions = relationship("Transaction", back_populates="carpooling")
