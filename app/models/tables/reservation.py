from sqlalchemy import Integer,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from databases.postgresql import Base

class Reservation(Base):

    __tablename__ = "carpooling_user"

    carpooling_id: Mapped[int] = mapped_column(ForeignKey("carpoolings.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    user = relationship("User",back_populates="reservations")
    carpooling = relationship("Carpooling",back_populates="reservations")