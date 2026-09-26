from fastapi import APIRouter, UploadFile, File, Form,  Depends, status, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from databases.postgresql import get_session
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from app.schemas.user_schema import UserCreate,UserRead, UserProfileUpdate, UserAccountUpdate, UserRoleUpdate
from app.schemas.change_password_schema import ChangePasswordSchema
from datetime import date

router = APIRouter(prefix="/users",tags=["users"])

def get_service_user(db: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(UserRepository(db), RoleRepository(db))

@router.get("/",response_model=list[UserRead])
async def list_users(service: UserService = Depends(get_service_user)):
    """
    Retrieves a list of all users.

    This endpoint fetches all users stored in the database and returns
    them in the format specified by the UserRead schema.

    Args:
        service (UserService, optional): The service layer for handling user-related operations.
        This is injected automatically using Depends(get_service_user).

    Returns:
        list[UserRead]: List of all users represented by the 'UserRead' schema which
        includes relevant user details such as name and ID.
    """
    return await service.get_all()

@router.get("/me",response_model=UserRead)
async def get_me(request: Request, service: UserService = Depends(get_service_user)):
    """
        Retrieve the current authenticated user.

        This endpoint fetches a user by its ID stored in the database and returns
        them in the format specified by the `UserRead` schema.

        Args:
            request (Request): Unique identifier of the user
            service (UserService, optional): The service layer for handling user-related operations.
                                            This is injected automatically using `Depends(get_user_service)`.

        Returns:
            user (UserRead): A user represented by the `UserRead`
                schema, which includes relevant user details such as name and ID.
        """
    user_id: int = request.state.user_id

    if user_id is None:
        raise HTTPException(401, "Unauthorized")

    return await service.get_user_with_roles(user_id)

@router.post("/",response_model=dict[str,str], status_code=status.HTTP_201_CREATED)
async def create_user( data: UserCreate, service: UserService = Depends(get_service_user)) -> dict[str,str]:
    """
    Creates a new user.

    Args:
        data (UserRegister): Schema containing all data required to create the user.
        service (UserService, optional): The service layer for handling user-related operations.
                                            This is injected automatically using `Depends(get_user_service)`.

    Returns:
        dict[str,str]: A dictionary containing a success message if the user was created successfully.
    """
    await service.create_user(data)
    return {"message":"User created successfully"}

@router.patch("/me/profile",response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_profile(request: Request, payload: UserProfileUpdate, service: UserService = Depends(get_service_user)):

    user_id: int = request.state.user_id

    return await service.update_profile(user_id, payload)

@router.patch("/me/account",response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_account(request: Request, payload: UserAccountUpdate, service: UserService = Depends(get_service_user)):
    user_id: int = request.state.user_id

    return await service.update_account(user_id, payload)

@router.patch("/me/roles",response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_roles(request: Request, payload: UserRoleUpdate, service: UserService = Depends(get_service_user)):
    user_id: int = request.state.user_id

    return await service.update_roles(user_id, payload)

@router.patch("/me/avatar",response_model=UserRead, status_code=status.HTTP_200_OK)
async def update_avatar(request: Request, avatar_file: UploadFile = File(...), service: UserService = Depends(get_service_user)):
    user_id: int = request.state.user_id

    return await service.update_avatar(user_id,avatar_file)

@router.put("/me/change-password",response_model=dict[str,str], status_code=status.HTTP_200_OK)
async def change_password(request: Request, passwords: ChangePasswordSchema , service: UserService = Depends(get_service_user)):
    """
    Change the password of a user in the database.
    Args:
        request (Request): Authenticated user identifier from request.
        passwords (PasswordsSchema): A schema containing passwords of the user to update.
        service (UserService, optional): The service layer for handling user-related operations.
                                            This is injected automatically using `Depends(get_user_service)`.

    Returns:
        dict[str,str]: A dictionary containing a success message if the password was modified successfully.
    """
    user_id: int = request.state.user_id
    await service.change_password_user(user_id,passwords)
    return {"message":"Password changed successfully"}



