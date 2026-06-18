from datetime import datetime
from sqlalchemy import Integer, String, DateTime, func
from sqlalchemy.orm import Mapped,mapped_column, relationship
from databases.postgresql import Base

class Brand(Base):
    """
    Represents a brand stored in the database.

    Attributes:
        id (int): The id of the brand stored in the database. Ex.: 1
        name (str): The name of the brand stored in the database. Ex.: 'renault'
        created_at (datetime): The date when the brand was created. Managed by the db. Ex.: 2019-04-01T12:00:00Z
        updated_at (datetime): The date when the brand was last updated. Managed by the db. Ex.: 2020-04-01T12:00:00Z

    Relationships:
        cars: All cars associated with the brand.

    Notes:
        - The name must not exceed 50 characters.
        - The name is required.
        - The name should be unique.
    """
    __tablename__ = 'brands'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relation one-to-many with Car entity
    cars = relationship("Car", back_populates="brand")