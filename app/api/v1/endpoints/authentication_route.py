from fastapi import APIRouter,  Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from databases.postgresql import get_session
from app.services.authentication_service import AuthenticationService
from app.repositories.user_repository import UserRepository
from app.schemas.login_schema import LoginSchema
from app.schemas.token_schema import TokenResponse
from app.utils.auth_utils import create_access_token

router = APIRouter(prefix="/auth",tags=["auth"])

def get_service_authentication(db: AsyncSession = Depends(get_session)) -> AuthenticationService:
    return AuthenticationService(UserRepository(db))

@router.post("/login")
async def login(
        credentials: LoginSchema,
        response: Response,
        service: AuthenticationService = Depends(get_service_authentication)
):
    """
    Args:
        credentials:
        response:
        service:

    Returns:

    """
    user = await service.authenticate_user(
        credentials.email,
        credentials.password
    )

    token = create_access_token(
        {"sub": str(user.id)}
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,      # True en production HTTPS
        samesite="lax",
        max_age=60 * 60
    )

    return {
        "message": "Login successful"
    }

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token")
    return {
        "message": "Logout successful"
    }