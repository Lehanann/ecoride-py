from fastapi import APIRouter, UploadFile, File, Form,  Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from databases.postgresql import get_session
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate,UserUpdate,UserRead
from app.schemas.change_password_schema import ChangePasswordSchema
from datetime import date

router = APIRouter(prefix="/user",tags=["user"])

def get_service_user(db: AsyncSession = Depends(get_session)) -> UserService:
    return UserService(UserRepository(db))

@router.get("/",response_model=list[UserRead])
async def list_users(service: UserService = Depends(get_service_user)):
    """
    Retrieves a list of all users from database.

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

@router.get("/{user_id}",response_model=UserRead)
async def get_user(user_id: int, service: UserService = Depends(get_service_user)):
    """
        Retrieve user by its ID from the database.

        This endpoint fetches a user by its ID stored in the database and returns
        them in the format specified by the `UserRead` schema.

        Args:
            user_id (int): Unique identifier of the user
            service (UserService, optional): The service layer for handling user-related operations.
                                            This is injected automatically using `Depends(get_user_service)`.

        Returns:
            user (UserRead): A user represented by the `UserRead`
                schema, which includes relevant user details such as name and ID.
        """
    return await service.get_by_id(user_id)

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
    Creates a new user in the database.
    Args:
        username (str): The username of the user to create.:
        email (str): The email of the user to create.:
        firstname (str, optional): The first name of the user to create.:
        lastname (str, optional): The last name of the user to create.:
        phone (str, optional): The phone number of the user to create.:
        address (str, optional): The address of the user to create.:
        birth_date(date, optional): The birthdate of the user to create.:
        password (str): The password of the user to create.:
        confirm_password (str): The confirmation password of the user to create.:
        avatar_file (UploadFile, optional): The file containing the avatar of the user to create.:
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

@router.patch("/{user_id}",response_model=dict[str,str], status_code=status.HTTP_200_OK)
async def update_user(
        user_id: int,
        username: str | None = Form(None),
        email: str | None = Form(None),
        firstname: str | None = Form(None),
        lastname: str | None = Form(None),
        phone: str | None = Form(None),
        address: str | None = Form(None),
        birth_date: date | None = Form(None),
        avatar_file: UploadFile = File(None),
        service: UserService = Depends(get_service_user)):
    """
    Updates an existing user in the database.
    Args:
        user_id (int): The id of the user to update.
        username (str, optional): The username of the user to update.
        email (str, optional): The email of the user to update.
        firstname (str, optional): The first name of the user to update.
        lastname (str, optional): The last name of the user to update.
        phone (str, optional): The phone number of the user to update.
        address (str, optional): The address of the user to update.
        birth_date (date, optional): The birthdate of the user to update.
        avatar_file (UploadFile, optional): The file containing the avatar of the user to update.
        service (UserService, optional): The service layer for handling user-related operations.
                                            This is injected automatically using `Depends(get_user_service)`.

    Returns:
        dict[str,str]: A dictionary containing a success message if the user was updated successfully.
    """

    raw_data = {
        "username": username,
        "email": email,
        "firstname": firstname,
        "lastname": lastname,
        "phone": phone,
        "address": address,
        "birth_date": birth_date,
    }

    data_dict = dict()

    for key, value in raw_data.items():
        if value is not None:
            data_dict[key] = value

    data = UserUpdate(**data_dict)

    await service.update_user(user_id, data, avatar_file)
    return {"message":"User updated successfully"}

@router.put("/{user_id}/change-password",response_model=dict[str,str], status_code=status.HTTP_200_OK)
async def change_password(user_id: int, passwords: ChangePasswordSchema , service: UserService = Depends(get_service_user)):
    """
    Change the password of a user in the database.
    Args:
        user_id (int): The id of the user to update.:
        passwords (PasswordsSchema): A schema containing passwords of the user to update.:
        service (UserService, optional): The service layer for handling user-related operations.
                                            This is injected automatically using `Depends(get_user_service)`.

    Returns:
        dict[str,str]: A dictionary containing a success message if the password was modified successfully.
    """
    await service.change_password_user(user_id,passwords)
    return {"message":"Password changed successfully"}



