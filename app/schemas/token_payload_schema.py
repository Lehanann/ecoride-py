from pydantic import BaseModel

class TokenPayload(BaseModel):
    """
    Schema representing the decoded payload contained
    within a JWT access token.

    Attributes:
        sub (str): Subject identifier of the authenticated
            user. Typically corresponds to the user ID.
        exp (int | None): Unix timestamp indicating the expiration time of the token.

    Note:
        This schema is intended for internal use when
        validating and decoding JWT tokens.
    """

    sub: str
    exp: int | None = None