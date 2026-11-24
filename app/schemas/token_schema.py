from pydantic import BaseModel

class TokenResponse(BaseModel):
    """
    Base schema used to  a token.
    """
    access_token: str
    token_type: str = 'bearer'