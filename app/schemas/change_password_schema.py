from pydantic import BaseModel, Field

class ChangePasswordSchema(BaseModel):
    """
    Schema for updating an existing user's password

    Attributes:
        old_password (str): Current password of user
        new_password (str): new password of user
        confirm_password (str): confirmation new password of user
    """
    old_password: str = Field(...,description="The current password of the user")
    new_password: str = Field(...,description="The new password of the user")
    confirm_password: str = Field(...,description="Confirm the new password of the user")
