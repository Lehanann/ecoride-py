from sqlalchemy import Integer, String, Date, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from databases.postgresql import Base
from datetime import date
from decimal import Decimal

class User(Base):
    """
    Represent a user stored int the database
    Attributes:
        id (int): The id of the user. Ex.: 1
        username (str): The username of the user. Ex.: 'jdoe'
        firstname (str): The first name of the user. Ex.: 'John'
        lastname (str): The last name of the user. Ex.: 'Doe'
        email (str): The email of the user. Ex.: 'jdoe@example.fr'
        password_hash (str): The password of the user. Ex. 'dfhrzegge5r4g5reg45er4gr5e4rt4'
        phone (str): The phone number of the user. Ex.: '0102030405'
        address (str): The address of the user Ex.: '24 rue de la République 75001 Paris'
        birth_date(date): Date of birth of the user.(YYYY-mm-dd) Ex: '1981-01-01'
        photo (str): Path photo of the user. Ex.: /storage/bb245fea5411zsz/e5rqd2d14.png
        credit (Numeric): The credit of the user. Ex.: 20
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    firstname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    lastname: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(10), nullable=True)
    address: Mapped[str | None] = mapped_column(String(250), nullable=True)
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    photo: Mapped[str | None] = mapped_column(String(254), nullable=True)
    credit: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, server_default='20')