from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped,mapped_column, relationship
from databases.postgresql import Base


class Brand(Base):
    """
    Represent a brand stored int the database.

    Attributes:
        id (int): The id of the brand stored int the database.
        name (str): The name of the brand stored int the database.
    Relationships:

    Notes:
        - The name contains 50 characters max.
        - The name is required.
    """
    __tablename__ = 'brands'

    id: Mapped[int]= mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str]= mapped_column(String(50), index=True)