import logging
from app.models.tables.user import User
from app.repositories.user_repository import UserRepository
from app.core.security.password_security import verify_password
from app.core.exceptions.http_exceptions import unauthorized

logger = logging.getLogger(__name__)

class AuthenticationService:
    """
    Authentication service that performs operations on authenticated users.
    """
    INVALID_CREDENTIALS = "Invalid credentials"

    def __init__(self, user_repository: UserRepository):
        """
        Initialize the user service with the user repository.

        Args:
            user_repository (UserRepository): The repository of the user.
        """
        self.user_repository = user_repository

    async def authenticate_user(self, email: str, password: str) -> User:
        """
        Authenticate a user using email and password.

        Args:
            email (str): User email.
            password (str): Plain text password.
        Returns:
            User | None:Returns the authenticated user if the credentials are valid, otherwise None.
        """
        user = await self.user_repository.get_by_email(email)
        if user is None:
            raise unauthorized(detail=self.INVALID_CREDENTIALS)

        if not verify_password(password, user.password_hash):
            raise unauthorized(detail=self.INVALID_CREDENTIALS)

        return user