from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from decimal import Decimal
from fastapi import UploadFile

class UserBase(BaseModel):
    """
    Base schema for the user, shared by create, update, and read operations and inherited by other schemas.

    Attributes:
        username (str): The username of the user.
        email (str): The email of the user.
        firstname (str): The first name of the user.
        lastname (str): The last name of the user.
        phone (str): The phone number of the user.
        address (str): The address of the user.
        birth_date(date): The date of birth of the user.
        credit (Decimal): The credit of the user.
    Notes:
        - The username field is required, and no more than 150 characters.
        - The email field is required, must be unique and no more than 254 characters
        - The firstname is optional and no more than 100 characters.
        - The lastname is optional and no more than 100 characters.
        - The phone number is optional, no more than 10 characters.
        - The address is optional and no more than 250 characters.
    """
    username: str = Field(..., max_length=150 , description="The username of the user.")
    email: str = Field(..., max_length=254, description="The email of the user.")
    firstname: str | None = Field(None,max_length=100, description="The first name of the user.")
    lastname: str | None = Field(None,max_length=100, description="The last name of the user.")
    phone: str | None = Field(None, max_length=10, description="The phone number of the user.")
    address: str | None = Field(None, max_length=250, description="The address of the user.")
    birth_date: date | None = Field(None, description="The date of birth of the user.")
    credit: Decimal = Field(..., description="The credit of the user.")

class UserCreate(UserBase):
    """
    Schema used to create a new user.
    Inherits all fields from UserBase schema.

    Attributes:
        password (str): The password of the user.
    Notes:
        - The password_hash field is required, must be at least 14 characters long and no more than 256 characters.
    """
    password: str = Field(...,min_length=14, max_length=256, description="The user's password (will be hashed).")
    photo: UploadFile | None = Field(None, description="Photo file to upload (optional).")


class UserUpdate(UserBase):
    """
    Schema for updating an existing user.

    All fields are optional. Only provided fields will be updated.
    The `credit` field is intentionally excluded to prevent direct modifications.

    Attributes:
        username (str | None): New username.
        email (str | None): New email.
        firstname (str | None): New first name.
        lastname (str | None): New last name.
        phone (str | None): New phone number.
        address (str | None): New address.
        birth_date (date | None): New date of birth.
        photo (str | None): New photo path.
        password (str | None): New password (will be hashed).
    Notes:
        - The username field is required, and no more than 150 characters.
        - The email field is required, must be unique and no more than 254 characters.
        - The firstname is optional and no more than 100 characters.
        - The lastname is optional and no more than 100 characters.
        - The phone number is optional, no more than 10 characters.
        - The address is optional and no more than 250 characters.
        - The birth_date is optional and no more than 254 characters.
        - The photo url is optional, no more than 254 characters.
        - The password is optional,at least 14 and no more than 254 characters.

    """
    username: str | None = Field(None, description="The username of the user.")
    email: str | None = Field(None, description="The email of the user.")
    firstname: str | None = Field(None, description="The first name of the user.")
    lastname: str | None = Field(None, description="The last name of the user.")
    phone: str | None = Field(None, description="The phone number of the user.")
    address: str | None = Field(None, description="The address of the user.")
    birth_date: date | None = Field(None, description="The date of birth of the user.")
    photo: UploadFile | None = Field(None, description="New photo file to upload (optional).")
    password: str | None = Field(None, min_length=14, max_length=256, description="New password (will be hashed)).")

class UserRead(UserBase):
    """
    Schema used when reading an existing user from the database.
    Inherits all fields from UserBase schema.

    Attributes:
        id: The id of the user.
        photo_url: The public URL of the user's photo.
    Notes:
        photo_url is optional, no more than 254 characters.
    """
    id: int
    photo_url : str | None = Field(None, description="Public URL of the user's photo.")

    model_config = ConfigDict(from_attributes=True)


