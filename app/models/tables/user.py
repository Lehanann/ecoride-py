from sqlalchemy import Integer, String, Date, Numeric, text, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from databases.postgresql import Base
from datetime import date, datetime
from decimal import Decimal
from app.models.association_tables import role_user

class User(Base):
    """
    Represents a user in the application.
    A user can have one or more roles (e.g. passenger, driver).
    Field is_active allows the soft delete of the user.

    Attributes:
        id (int): The unique identifier of the user. Ex.: 1
        username (str): The username of the user. Ex.: 'jdoe'
        firstname (str): The first name of the user. Ex.: 'John'
        lastname (str): The last name of the user. Ex.: 'Doe'
        email (str): The email of the user. Ex.: 'jdoe@example.fr'
        password_hash (str): Hashed password of the user. Ex. 'dfhrzegge5r4g5reg45er4gr5e4rt4'
        phone (str): The phone number of the user. Ex.: '0102030405'
        address (str): The address of the user. Ex.: '24 rue de la République 75001 Paris'
        birth_date (date): Date of birth of the user. (YYYY-MM-DD) Ex: '1981-01-01'
        avatar_url (str): Path to the user's profile picture. Ex.: /storage/bb245fea5411zsz/e5rqd2d14.png
        credit (Numeric): The credit of the user. Ex.: 20.00
        created_at (datetime): The date when the user was created. Managed by the db.
        updated_at (datetime): The date when the user was last updated. Managed by the db.
        is_active (bool): Whether the user is active, default true. Ex.: True
        deleted_at (datetime): The date when the user was deleted. Managed by the db.

    Relationships:
        cars: The cars associated to a user.
        roles: The roles associated to a user.
        reservations: The reservations associated to a user.
        opinions_given: Opinions created by the user.
        opinions_received: Opinions received by the user.
        opinions_validated: Opinions validated by the user.
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
    avatar_url: Mapped[str | None] = mapped_column(String(254), nullable=True)
    credit: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False, server_default=text('20.00'))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False,server_default=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relation one-to-many with Car entity.
    cars = relationship("Car", back_populates="user")
    # Relation many-to-many with Role entity.
    roles = relationship("Role", secondary=role_user, back_populates="users")
    # Relation one-to-many with Reservation entity.
    reservations = relationship("Reservation", back_populates="user")
    # Relation one-to-many with Opinion entity
    opinions_given = relationship(
        "Opinion",
        foreign_keys="Opinion.author_id",
        back_populates="author"
    )
    # Relation one-to-many Opinion entity
    opinions_received = relationship(
        "Opinion",
        foreign_keys="Opinion.target_id",
        back_populates="target"
    )
    # Relation one-to-many with Opinion entity
    opinions_validated = relationship(
        "Opinion",
        foreign_keys="Opinion.validator_id",
        back_populates="validator"
    )
    # Relation one-to-many with Transaction entity
    transactions = relationship("Transaction", back_populates="user")