from sqlalchemy import Integer, String, Date, Time, ForeignKey, Numeric, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from databases.postgresql import Base
from datetime import date, time
from sqlalchemy.dialects.postgresql import ENUM
from app.utils.carpooling_status_enum import CarpoolingStatusEnum
from decimal import Decimal

class Carpooling(Base):
    """
    Represents a carpooling stored int the database.
    Attributes:
        id (int): The ID of the carpooling. Ex.: 1
        departure_date (date): The date of the departure of the carpooling. Ex.: '2020-04-01' YYYY-MM-DD
        departure_time (time): The time of the departure of the carpooling. Ex.: '07:00'
        departure_location (str): The location of the departure of the carpooling. Ex.: '15 av. Mystery 69999 Les-Orchidés'
        end_date (date): The date of the end of the carpooling. Ex.: '2020-04-01' YYYY-MM-DD
        end_time (time): The time of the end of the carpooling. Ex.: '07:40'
        end_location (str): The location of the end of the carpooling. Ex.: '39 Bis impasse des Secrets 69899 Le Bois-Enchanté'
        status (CarpoolingStatusEnum): The status of the carpooling initialized to draft by the db. Ex.: 'draft'
        place_number (int): The place number available of the carpooling. Ex.: 2
        price (Decimal): The price of the carpooling, minimum 2 credits. Ex.: 4
        car_id (int): The ID of the car used for the carpooling. Ex.: 12
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
                                                              name="carpooling_status_enum",
                                                              create_type=False),
                                                         nullable=False,
                                                         server_default=text("'draft'"))
    place_number: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(6,2), nullable=False)
    car_id: Mapped[int] = mapped_column(Integer, ForeignKey('cars.id'), nullable=False)

    car = relationship("Car", back_populates="carpoolings")

    reservations = relationship("Reservation", back_populates="carpooling")