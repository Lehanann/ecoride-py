from sqlalchemy import Integer, Text, ForeignKey, DateTime, text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ENUM
from databases.postgresql import Base
from app.utils.opinion_status_enum import OpinionStatusEnum
from datetime import datetime

class Opinion(Base):
    """
    Represents an opinion left by a passenger about a driver after a carpooling.

    Attributes:
        id (int): Unique identifier of the opinion. Ex.: 1
        comment (str): Textual feedback provided by the author. Ex.: "Driver was very friendly"
        note (int): Rating given to the driver. Ex.: 4
        status (OpinionStatusEnum): Current status of the opinion (pending, approved, rejected). Ex.: 'pending'
        carpooling_id (int): Identifier of the related carpooling. Ex.: 5
        author_id (int): Identifier of the user who wrote the opinion (passenger). Ex.: 135
        target_id (int): Identifier of the user being reviewed (driver). Ex.: 12
        validator_id (int | None): Identifier of the employee who validated the opinion. Ex.: 232
        validated_at (datetime | None): Timestamp when the opinion was validated. Ex.: 2019-04-01T12:00:00Z
        created_at (datetime): The date when the opinion was created. Managed by the db. Ex.: 2019-04-01T12:00:00Z

    Relationships:
        author: The user who created the opinion (passenger).
        target: The user who receives the opinion (driver).
        validator: The employee who reviewed and validated the opinion.
        carpooling: The carpooling related to the opinion.

    Notes:
        - comment, note, status, carpooling_id, author_id, target_id are required.
        - note must be between 1 and 5
    """
    __tablename__ = 'opinions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    note: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[OpinionStatusEnum] = mapped_column(ENUM(OpinionStatusEnum,
                                                           name="opinion_status",
                                                           create_type=False,
                                                           ),
                                                      nullable=False,
                                                      server_default=text("'pending'"))
    carpooling_id: Mapped[int] = mapped_column(Integer, ForeignKey("carpoolings.id"), nullable=False)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    target_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    validator_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"),nullable=True)
    validated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    author = relationship("User", foreign_keys=[author_id], back_populates="opinions_given")
    target = relationship("User", foreign_keys=[target_id], back_populates="opinions_received")
    validator = relationship("User", foreign_keys=[validator_id], back_populates="opinions_validated")
    carpooling = relationship("Carpooling", back_populates="opinions")
