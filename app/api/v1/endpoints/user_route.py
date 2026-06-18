from fastapi import APIRouter, UploadFile, File, Form,  Depends, status, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from databases.postgresql import get_session
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from app.schemas.user_schema import UserCreate,UserUpdate,UserRead
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
async def create_user(
        username: str = Form(...),
        email: str = Form(...),
        firstname: str | None= Form(None),
        lastname: str | None= Form(None),
        phone: str | None= Form(None),
        address: str | None= Form(None),
        birth_date: date | None = Form(None),
        password: str = Form(...),
        confirm_password: str = Form(...),
        avatar_file: UploadFile | None = File(None),
        service: UserService = Depends(get_service_user)) -> dict[str,str]:
    """
    Creates a new user.

    Args:
        username (str): The username of the user.
        email (str): The unique email of the user.
        firstname (str, optional): The first name of the user.
        lastname (str, optional): The last name of the user.
        phone (str, optional): The phone number of the user.
        address (str, optional): The address of the user.
        birth_date(date, optional): The birthdate of the user.
        password (str): The password of the user.
        confirm_password (str): The confirmation password of the user.
        avatar_file (UploadFile, optional): The file containing the avatar of the user.
        service (UserService, optional): The service layer for handling user-related operations.
                                            This is injected automatically using `Depends(get_user_service)`.

    Returns:
        dict[str,str]: A dictionary containing a success message if the user was created successfully.
    """

    data = UserCreate(**{
        "username": username,
        "email": email,
        "firstname": firstname,
        "lastname": lastname,
        "phone": phone,
        "address": address,
        "birth_date": birth_date,
        "password": password,
        "confirm_password": confirm_password,
    })

    await service.create_user(data, avatar_file)
    return {"message":"User created successfully"}

@router.patch("/me",response_model=dict[str,str], status_code=status.HTTP_200_OK)
async def update_user(
        request: Request,
        username: str | None = Form(None),
        email: str | None = Form(None),
        firstname: str | None = Form(None),
        lastname: str | None = Form(None),
        phone: str | None = Form(None),
        address: str | None = Form(None),
        birth_date: date | None = Form(None),
        avatar_file: UploadFile | None = File(None),
        roles: list[str] | None = Form(None),
        service: UserService = Depends(get_service_user)):
    """
    Updates an existing user in the database.
    Args:
        request (Request): containing auth user information.
        username (str, optional): The username of the user.
        email (str, optional): The email of the user.
        firstname (str, optional): The first name of the user.
        lastname (str, optional): The last name of the user.
        phone (str, optional): The phone number of the user.
        address (str, optional): The address of the user.
        birth_date (date, optional): The birthdate of the user.
        avatar_file (UploadFile, optional): The file containing the avatar of the user.
        roles (list[str], optional): The roles of the user.
        service (UserService, optional): The service layer for handling user-related operations.
                                            This is injected automatically using `Depends(get_user_service)`.

    Returns:
        dict[str,str]: A dictionary containing a success message if the user was updated successfully.
    """
    user_id: int = request.state.user_id
    raw_data = {
        "username": username,
        "email": email,
        "firstname": firstname,
        "lastname": lastname,
        "phone": phone,
        "address": address,
        "birth_date": birth_date,
        "roles": roles,
    }

    data_dict = dict()

    for key, value in raw_data.items():
        if value is not None:
            data_dict[key] = value

    data = UserUpdate(**data_dict)

    await service.update_user(user_id, data, avatar_file)
    return {"message":"User updated successfully"}

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



