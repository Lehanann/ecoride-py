from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from databases.postgresql import Base
from app.models.association_tables import role_user

class Role(Base):
    """
     Represents a car stored in the database.
     Attributes:
         id (int): The ID of the role stored in the database.
         name (str): The name of the role stored in the database.
     Notes:
         - The name must not exceed 50 characters.
         - The name is required.
     """
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    users = relationship("User", secondary=role_user,back_populates="roles")