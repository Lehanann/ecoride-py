from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from databases.postgresql import Base
from app.models.association_tables import role_user

class Role(Base):
    """
     Represents a user role in the application (e.g. admin, passenger, driver, employee).

     Attributes:
         id (int): The unique identifier of the role.
         name (str): The name of the role.

     Relationships:
        users: Users associated with the role.

     Notes:
         - The name should be unique.
         - The name must not exceed 50 characters.
         - The name is required.
     """
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)

    users = relationship("User", secondary=role_user, back_populates="roles")