from pydantic import BaseModel, Field, ConfigDict

class BrandBase(BaseModel):
    """
    Base schema for the brand, shared by create, update, and read operations and inherited by other schemas.

    Attributes:
        name(str): The name of the brand.
    Notes:
        - The name of the brand must be unique.
        - the name must not exceed 50 characters.
        - The name is required
    """
    name: str = Field(...,max_length=50, description="The name of the brand.")

class BrandCreate(BrandBase):
    """
    Schema used when creating a new brand.

    Inherits all fields from BrandBase schema.
    """
    pass

class BrandUpdate(BaseModel):
    """
    Schema used when updating an existing brand.

    All fields inherited from BrandBase become optional.
    Only fields provided in the request will be updated.

    Attributes:
        name(str | None): The name of the brand.

    Notes:
        - .
    """
    name: str | None = Field(None,max_length=50, description="The name of the brand.")

class BrandRead(BrandBase):
    """
        Schema used when reading an existing brand from the database.
        Inherits all fields from BrandBase schema.

        Attributes:
            id (int): The id of the user.
    """
    id: int = Field(..., description="The id of the user.")

    model_config = ConfigDict(from_attributes=True)