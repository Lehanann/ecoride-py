from pydantic import BaseModel, Field, EmailStr


class LoginSchema(BaseModel):
    """
    Schema representing authentication credentials.

    Attributes:
        email (EmailStr): Email address of the user.
        password (str): Plain text password provided by the user.
    """

    email: EmailStr = Field(..., description="Email address of the user.")
    password: str = Field(..., description="Password of the user.")
