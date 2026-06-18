from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import date
from decimal import Decimal


class UserBase(BaseModel):
    """
    Base schema for the user, shared by create, update, and read operations and inherited by other schemas.

    Attributes:
        username (str): The username of the user.
        email (EmailStr): The email of the user.
        firstname (str): The first name of the user.
        lastname (str): The last name of the user.
        phone (str): The phone number of the user.
        address (str): The address of the user.
        birth_date(date): The date of birth of the user.
        avatar_url (str): The public URL of the user's photo.

    Notes:
        - The username field is required, and no more than 150 characters.
        - The email field is required, must be unique and no more than 254 characters
        - The firstname is optional and no more than 100 characters.
        - The lastname is optional and no more than 100 characters.
        - The phone number is optional, no more than 10 characters.
        - The address is optional and no more than 250 characters.
        - The avatar_url field is optional and no more than 254 characters.
    """
    username: str = Field(..., max_length=150 , description="The username of the user.")
    email: EmailStr = Field(..., description="The email of the user.")
    firstname: str | None = Field(None,max_length=100, description="The first name of the user.")
    lastname: str | None = Field(None,max_length=100, description="The last name of the user.")
    phone: str | None = Field(None, max_length=10, description="The phone number of the user.")
    address: str | None = Field(None, max_length=250, description="The address of the user.")
    birth_date: date | None = Field(None, description="The date of birth of the user.")
    avatar_url: str | None = Field(None, max_length=254, description="The public URL of the user's photo.")

class UserCreate(UserBase):
    """
    Schema used to create a new user.

    Inherits all fields from UserBase schema.

    Attributes:
        password (str): The password of the user.

    Notes:
        - The password field is required and must be at least 14 characters long and no more than 256 characters.
        - confirm_password field is required, must match the password.
    """
    password: str = Field(...,min_length=14, max_length=256, description="The user's password will be created and hashed.")
    confirm_password: str = Field(...,min_length=14, max_length=256, description="The confirm user's password will be created and hashed.")


class UserUpdate(BaseModel):
    """
    Schema for updating an existing user.

    Only provided fields will be updated.
    The `credit` field is intentionally excluded to prevent direct modifications.

    Attributes:
        username (str | None): New username.
        email (EmailStr | None): New email.
        firstname (str | None): New first name.
        lastname (str | None): New last name.
        phone (str | None): New phone number.
        address (str | None): New address.
        birth_date (date | None): New date of birth.
        avatar_url (str | None): New public URL of the user's photo.

    Notes:
        - All fields are optional.
        - Only provided fields will be updated.
    """
    username: str | None = Field(None, max_length=150, description="The username of the user.")
    email: EmailStr | None = Field(None, description="The email of the user.")
    firstname: str | None = Field(None, max_length=100, description="The first name of the user.")
    lastname: str | None = Field(None, max_length=100, description="The last name of the user.")
    phone: str | None = Field(None, max_length=10, description="The phone number of the user.")
    address: str | None = Field(None, max_length=250, description="The address of the user.")
    birth_date: date | None = Field(None, description="The date of birth of the user.")
    avatar_url: str | None = Field(None, max_length=254, description="The public URL of the user's photo.")
    roles: list[str] | None = Field(None, min_length=1, description="The roles of the user.")

class RoleRead(BaseModel):
    """
    Schema used to read a role.

    Attributes:
        id (int): The id of the role.
        name (str): The name of the role.
    """
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class UserRead(UserBase):
    """
    Schema used when reading an existing user from the database.

    Inherits all fields from UserBase schema.

    Attributes:
        id (int): The id of the user.
        avatar_url (str): The public URL of the user's photo.
        credit (Decimal): The credit of the user.
        roles (list[str]): The roles of the user.
    """
    id: int
    credit: Decimal = Field(...,max_digits=6, decimal_places=2, description="The credit of the user.")
    roles: list[RoleRead] = Field(..., description="The roles of the user.")
    model_config = ConfigDict(from_attributes=True)
