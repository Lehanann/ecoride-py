from sqlalchemy import Integer,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from databases.postgresql import Base

class Reservation(Base):
    """
    Represents an association between users and carpoolings.
    Each record links one user to one carpooling.

    Attributes:
        carpooling_id (int): The identifier of the carpooling.
        user_id (int): The identifier of the user.

    Relationships:
        user: Participant of the carpooling.
        carpooling: The carpooling associated with the participant

    Notes:
        - Primary keys are user_id and carpooling_id and reference User and Carpooling entities.
        - A user can join multiple carpoolings.
        - Carpooling can have multiple users.
        - This table represents a many-to-many relation.
    """
    __tablename__ = "carpoolings_users"

    carpooling_id: Mapped[int] = mapped_column(ForeignKey("carpoolings.id"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)

    user = relationship("User",back_populates="reservations")
    carpooling = relationship("Carpooling",back_populates="reservations")