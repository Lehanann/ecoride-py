from fastapi import UploadFile, HTTPException, status
from psycopg import IntegrityError

from app.models.tables.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.change_password_schema import ChangePasswordSchema
from app.schemas.user_schema import UserCreate,UserUpdate
from app.services.file_service import FileService
from app.core.security.password_security import create_password_hash, verify_password
from app.models.tables.role import Role
from repositories.role_repository import RoleRepository


class UserService:
    """
    User service that performs operations on the user repository such as reading; creating, updating, and deleting users.
    """
    def __init__(self, repository: UserRepository, role_repository: RoleRepository):
        """
        Initialize the user service with the user repository.
        :param repository:
        """
        self.repository = repository
        self.role_repository = role_repository

    async def get_by_id(self, user_id: int) -> User | None:
        """
        Get a user from the repository by its id.
        Args:
            user_id(int): The ID of the user.
        Raises:
            HTTPException: if the ID of user is not found.
        Returns:
             user(User): The user with the given ID.
        """
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def get_all(self) -> list[User]:
        """
        Get all users from the repository.

        Raises:
            HTTPException: if the list of users is empty.

        Returns:
            list[User]: The list of users in the repository.
        """

        return await self.repository.get_all()

    async def create_user(self, data: UserCreate, avatar: UploadFile | None) -> User:
        """
        Create a new user in the repository
        Args:
            data (UserCreate): The schema containing fields to create new instance user.
            avatar (UploadFile): The file uploaded new user's avatar. if file exists save the file into storage and get url path
        Raises:
            HTTPException: if the new user is already created.
        Returns:
             user(User): The newly created instance of user.
        """

        if data.confirm_password != data.password:
            raise HTTPException(status_code=400, detail="Password and confirm_password are not equal")

        password_hash: str = create_password_hash(data.password)  # hash the password before creating user

        avatar_url: str | None = None

        if avatar:
            avatar_url: str = FileService.save_profile_image(avatar)

        dataform = {
            "username": data.username,
            "email": data.email,
            "password_hash": password_hash,
        }

        # Champs optionnels
        optional_fields = {
            "firstname": data.firstname,
            "lastname": data.lastname,
            "phone": data.phone,
            "address": data.address,
            "birth_date": data.birth_date,
            "avatar_url": avatar_url,
        }

        for key, value in optional_fields.items():
            if value is not None:
                dataform[key] = value

        try:
            created_user = await self.repository.create(dataform)
            role = await self.role_repository.get_by_name("passenger")
            if role is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
            created_user.roles.append(role)
            await self.repository.db.commit()
            return created_user
        except IntegrityError:
            await self.repository.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)


    async def update_user(self, user_id: int, data: UserUpdate, avatar: UploadFile | None) -> User | None:
        """
        Update an existing user in the repository.

        Args:
            user_id (int): The ID of the user to update.
            data (UserUpdate): The schema containing fields to update an instance user.
            avatar (UploadFile):

        Raises:

        Returns:
        """
        dataform = data.model_dump(exclude_unset=True)

        if avatar is not None:
            avatar_url: str | None = FileService.save_profile_image(avatar)
            dataform['avatar_url'] = avatar_url

        try:
            update_user = await self.repository.update(user_id, dataform)

            if update_user is None:
                raise HTTPException(status_code=404, detail="User not found")

            if "roles" in dataform:
                new_roles = []
                for role in dataform["roles"]:
                    if role not in ["passenger","driver"]:
                        raise HTTPException(status_code=400, detail="Role not found")
                    role_data = await self.role_repository.get_by_name(role)
                    if role_data is None:
                        raise HTTPException(status_code=400, detail="Role not found")
                    new_roles.append(role_data)
                update_user.roles = new_roles

            await self.repository.db.commit()
            return update_user
        except IntegrityError:
            await self.repository.db.rollback()
            raise HTTPException(status_code=400, detail="Error updating user")

    async def change_password_user(self, user_id: int, passwords: ChangePasswordSchema) -> str:
        """
        Modifying a user's password in the repository.
        Args:
            user_id (int): The ID of the user to modify.:
            passwords(ChangePasswordSchema): The schema containing fields to modify an instance of user's password.:

        Returns:

        """
        user = await self.repository.get_by_id(user_id)
        dataform = dict()

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if passwords.confirm_password != passwords.new_password:
            raise HTTPException(status_code=400, detail="new Password and confirm_password are not equal")

        if not verify_password(passwords.old_password, user.password_hash):
            raise HTTPException(status_code=400, detail="The old password is incorrect")

        hashed_password: str = create_password_hash(passwords.new_password)
        dataform['password_hash'] = hashed_password

        try:
            await self.repository.update(user_id, dataform)
            return "Password changed successfully"
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=400, detail="Error updating user")

    async def delete_user(self, user_id: int) -> None:
        """
        Delete an existing user in the repository.
        Args:
            user_id:

        Returns:

        """
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        try:
            await self.repository.delete(user_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Error deleting user")
