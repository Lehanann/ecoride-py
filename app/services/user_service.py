import logging
from sqlalchemy.exc import IntegrityError
from app.core.exceptions.http_exceptions import bad_request, not_found, conflict
from fastapi import UploadFile
from app.models.tables.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.change_password_schema import ChangePasswordSchema
from app.schemas.user_schema import UserCreate,UserUpdate
from app.services.file_service import FileService
from app.core.security.password_security import create_password_hash, verify_password
from app.repositories.role_repository import RoleRepository

logger = logging.getLogger(__name__)

class UserService:
    """
    User service that performs operations on the user repository such as reading; creating, updating, and deleting users.

    Attributes:
        Business rules:
            - User roles are limited to 'passenger' and 'driver'
    """
    DEFAULT_ROLE = "passenger"
    ALLOWED_USER_ROLES = frozenset ({
        "passenger",
        "driver",
    })
    USER_NOT_FOUND = "User not found"
    ROLE_NOT_FOUND = "Role not found"
    USER_ALREADY_EXISTS = "User already exists"
    PASSWORDS_NOT_MATCH = "Password and confirm password do not match"
    WRONG_OLD_PASSWORD = "The old password is incorrect"

    def __init__(self, user_repository: UserRepository, role_repository: RoleRepository):
        """
        Initialize the user service with the user repository.

        Args:
            user_repository (UserRepository): The repository of the user.
            role_repository (RoleRepository): The repository of the role.
        """
        self.user_repository = user_repository
        self.role_repository = role_repository

    async def get_by_id(self, user_id: int) -> User | None:
        """
        Retrieve an active user by its ID.

        Args:
            user_id (int): The ID of the user.

        Raises:
            HTTPException: If the user is not found.

        Returns:
            User: The user with the given ID.
        """
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise not_found(detail=self.USER_NOT_FOUND)
        return user

    async def get_all(self) -> list[User]:
        """
        Retrieve all active users.

        Returns:
            list[User]: The list of active users.
        """
        return await self.user_repository.get_all()

    async def create_user(self, data: UserCreate, avatar: UploadFile | None) -> User:
        """
        Create a new user.

        Args:
            data (UserCreate): The data required to create a user.
            avatar (UploadFile | None): Optional avatar file.

        Raises:
            not_found:
                - If default role is not found.
            bad_request:
                - If passwords do not match.
                - If an error occurs while creating a user.
            conflict:
                - If a user already exists.

        Returns:
            User: The newly created user.
        """
        if data.confirm_password != data.password:
            raise bad_request(detail=self.PASSWORDS_NOT_MATCH)

        password_hash: str = create_password_hash(data.password)  # hash the password before creating user

        avatar_url: str | None = None

        if avatar:
            avatar_url = FileService.save_profile_image(avatar)

        user_data = {
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
                user_data[key] = value

        try:
            created_user = await self.user_repository.create(user_data)
            role = await self.role_repository.get_by_name(self.DEFAULT_ROLE)
            if role is None:
                raise not_found(detail=self.ROLE_NOT_FOUND)
            created_user.roles.append(role)
            await self.user_repository.db.commit()
            return created_user
        except IntegrityError:
            await self.user_repository.db.rollback()
            logger.exception("Integrity error while creating a user")
            raise conflict(detail=self.USER_ALREADY_EXISTS)
        except Exception:
            await self.user_repository.db.rollback()
            logger.exception("Unexpected Error while creating a user")
            raise bad_request(detail="Error creating user")


    async def update_user(self, user_id: int, data: UserUpdate, avatar: UploadFile | None) -> User:
        """
        Update an existing user.

        Args:
            user_id (int): The ID of the user to update.
            data (UserUpdate): The fields to update.
            avatar (UploadFile | None): Optional avatar file.

        Raises:
            not_found:
                - If default role is not found.
                - if the user is not found.
            bad_request:
                - If an error occurs while updating a user.
            conflict:
                - If a user already exists.

        Returns:
            User: The updated user.
        """
        user_data = data.model_dump(exclude_unset=True)

        existing_user = await self.user_repository.get_by_id(user_id)
        if existing_user is None:
            raise not_found(detail=self.USER_NOT_FOUND)

        if avatar is not None:
            avatar_url = FileService.replace_profile_image(avatar, existing_user.avatar_url)
            user_data['avatar_url'] = avatar_url

        new_roles = None
        if "roles" in user_data:
            new_roles = []
            for role in user_data["roles"]:
                if role not in self.ALLOWED_USER_ROLES:
                    raise not_found(detail=self.ROLE_NOT_FOUND)
                role_data = await self.role_repository.get_by_name(role)
                if role_data is None:
                    raise not_found(detail=self.ROLE_NOT_FOUND)
                new_roles.append(role_data)

        try:
            updated_user = await self.user_repository.update(user_id, user_data)

            if updated_user is None:
                raise not_found(detail=self.USER_NOT_FOUND)

            if new_roles is not None:
                updated_user.roles = new_roles

            await self.user_repository.db.commit()
            return updated_user
        except IntegrityError:
            await self.user_repository.db.rollback()
            logger.exception("Integrity error while updating a user")
            raise conflict(detail=self.USER_ALREADY_EXISTS)
        except Exception:
            await self.user_repository.db.rollback()
            logger.exception("Unexpected Error while updating user")
            raise bad_request(detail="Error updating user")

    async def change_password_user(self, user_id: int, passwords: ChangePasswordSchema) -> str:
        """
        Change a user's password.

        Args:
            user_id (int): The ID of the user.
            passwords (ChangePasswordSchema): Password change data.

        Raises:
            not_found:
                - If the user is not found.
            bad_request:
                - If passwords do not match.
                - If the old password is incorrect.
                - If an error occurs while updating the user.
            conflict:
                - If a user already exists.

        Returns:
            str: Success message.
        """
        user = await self.user_repository.get_by_id(user_id)
        user_data = dict()

        if user is None:
            raise not_found(detail=self.USER_NOT_FOUND)

        if passwords.confirm_password != passwords.new_password:
            raise bad_request(detail=self.PASSWORDS_NOT_MATCH)

        if not verify_password(passwords.old_password, user.password_hash):
            raise bad_request(detail=self.WRONG_OLD_PASSWORD)

        hashed_password: str = create_password_hash(passwords.new_password)
        user_data['password_hash'] = hashed_password

        try:
            await self.user_repository.update(user_id, user_data)
            await self.user_repository.db.commit()
            return "Password changed successfully"
        except IntegrityError:
            await self.user_repository.db.rollback()
            logger.exception("Integrity error while changing password")
            raise conflict(detail=self.USER_ALREADY_EXISTS)
        except Exception:
            await self.user_repository.db.rollback()
            logger.exception("Unexpected Error while updating a user")
            raise bad_request(detail="Error updating user")

    async def delete_user(self, user_id: int) -> dict:
        """
        Soft delete a user.

        Sets `is_active` to False and records deletion timestamp.

        Args:
            user_id (int): The ID of the user to delete.

        Raises:
            not_found:
                - If the user is not found.
            bad_request:
                - If an error occurs during deletion.

        Returns:
            dict: Confirmation message.
        """
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise not_found(detail=self.USER_NOT_FOUND)
        try:
            await self.user_repository.delete(user_id)
            await self.user_repository.db.commit()
            return {"message": "User deleted successfully"}
        except Exception:
            await self.user_repository.db.rollback()
            logger.exception("Unexpected Error while deleting a user")
            raise bad_request(detail="Error deleting user")