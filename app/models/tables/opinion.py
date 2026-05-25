from sqlalchemy import Integer, Text, ForeignKey, DateTime, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM
from databases.postgresql import Base
from app.utils.opinion_status_enum import OpinionStatusEnum
from datetime import datetime

class Opinion(Base):
    """
    Represents an opinion left by a passenger about a driver after a carpooling.

    Attributes:
        id (int): Unique identifier of the opinion. Example: 1
        comment (str): Textual feedback provided by the author. Example: "Driver was very friendly"
        note (int): Rating given to the driver. Example: 4
        status (OpinionStatusEnum): Current status of the opinion (pending, approved, rejected)
        carpooling_id (int): Identifier of the related carpooling. Example: 5
        author_id (int): Identifier of the user who wrote the opinion (passenger). Example: 135
        target_id (int): Identifier of the user being reviewed (driver). Example: 12
        validator_id (int | None): Identifier of the employee who validated the opinion. Example: 232
        validated_at (datetime | None): Timestamp when the opinion was validated. Example: 2020-04-04 10:35:20

    Relationships:
        author: The user who created the opinion (passenger).
        target: The user who receives the opinion (driver).
        validator: The employee who reviewed and validated the opinion.
        carpooling: The carpooling related to the opinion.
    """
    __tablename__ = 'opinions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    note: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[OpinionStatusEnum] = mapped_column(ENUM(OpinionStatusEnum,
                                                           name="opinion_status_enum",
                                                           create_type=False,
                                                           ),
                                                      nullable=False,
                                                      server_default=text("'pending'"))
    carpooling_id: Mapped[int] = mapped_column(Integer, ForeignKey("carpoolings.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    target_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    validator_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"),nullable=True)
    validated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    author = relationship("User", foreign_keys=[author_id], back_populates="opinions_given")
    target = relationship("User", foreign_keys=[target_id], back_populates="opinions_received")
    validator = relationship("User", foreign_keys=[validator_id], back_populates="opinions_validated")
    carpooling = relationship("Carpooling", back_populates="opinions")
