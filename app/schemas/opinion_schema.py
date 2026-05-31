from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.utils.opinion_status_enum import OpinionStatusEnum

class OpinionBase(BaseModel):
    """
    Base schema for opinions, shared across create, update, and read operations.

    Attributes:
        comment (str): Textual feedback provided in the opinion.
        note (int): Rating given in the opinion (between 1 and 5).
        carpooling_id (int): Identifier of the related carpooling.

    Notes:
        - The note must be between 1 and 5.
    """
    comment: str = Field(..., description="Opinion comment.")
    note: int = Field(..., ge=1, le=5, description="Opinion note (1-5).")
    carpooling_id: int = Field(..., description="Associated carpooling ID.")

class OpinionCreate(OpinionBase):
    """
    Schema used to create a new opinion.

    Inherits all fields from OpinionBase.
    """
    pass

class OpinionStatusUpdate(BaseModel):
    """
    Schema used to update the status of an opinion.

    Attributes:
        status (OpinionStatusEnum): New status of the opinion (approved or rejected).
    """
    status: OpinionStatusEnum = Field(..., description="Opinion status.")

class OpinionRead(OpinionBase):
    """
    Schema used when reading an opinion from the database.

    Inherits all fields from OpinionBase.

    Attributes:
        id (int): Unique identifier of the opinion.
        status (OpinionStatusEnum): Current status of the opinion.
        validator_id (int | None): Identifier of the validator who validated the opinion(if validated).
        validated_at (datetime | None): Timestamp when the opinion was validated

    Notes:
        - id and status are always present.
        - validator_id and validated_at are optional until validation occurs.

    """
    id: int = Field(..., description="Opinion ID.")
    status: OpinionStatusEnum = Field(..., description="Opinion status.")
    validator_id: int | None = Field(None, description="Validator user ID.")
    validated_at: datetime | None = Field(None, description="Validation timestamp.")

    model_config = ConfigDict(from_attributes=True)
