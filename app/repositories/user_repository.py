from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tables.user import User
from typing import List
from datetime import datetime, UTC


class UserRepository:
    """
    User repository providing CRUD operations for a given SQLAlchemy model.
    """
    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the User repository with database session.

        Args:
            db (AsyncSession): Asynchronous database session.
        """
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        """
        Retrieve a user instance by its ID

        Args:
            user_id: Yhe unique identifier of the user.
        Returns:
            User | None: The user instance if found, otherwise None.
        """
        result = await self.db.execute(select(User).where(User.id == user_id).where(User.is_active == True))
        return result.scalars().one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """
        Retrieve a user instance by its email.

        Args:
            email (str): the email of user.
        Returns:
             User | None: The user instance if found, otherwise None.
        """
        result = await self.db.execute(select(User).where(User.email == email).where(User.is_active == True))
        return result.scalars().one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """
        Retrieve a user instance by its username.

        Args:
            username (str): The username of user.
        Returns:
             User | None: The user instance if found, otherwise None.
        """
        result = await self.db.execute(select(User).where(User.username == username).where(User.is_active == True))
        return result.scalars().one_or_none()

    async def get_all(self) -> List[User]:
        """
        Retrieve all instances of user from the database.

        Returns:
            list[User]: The List of all user's instances.
        """
        return list(await self.db.scalars(select(User).where(User.is_active == True)))

    async def create(self, data: dict) -> User:
        """
        Create a new user instance, with the password hashed

        Args:
            data (dict): Schema containing fields to create the user instance.
        Returns:
             user(User): The new user instance.
        """
        user = User(**data)
        self.db.add(user)
        return user

    async def update(self,user_id: int, data: dict) -> User | None:
        """
        Update an existing user instance by its ID.

        Args
            user_id(int): The user ID to update.
            data (UserUpdate): Schema containing fields to update the user instance.

        Returns:
             user(User): The updated user instance.
        Side Effects:
            Commits changes to the database and refreshes the user instance.
        """

        user = await self.get_by_id(user_id)
        if user is None:
            return None

        for key, value in data.items():
            setattr(user, key, value)

        return user

    async def delete(self, user_id: int) -> User| None:
        """
        Delete an existing user instance by its ID.

        Args:
            user_id(int): The user ID to delete.

        Returns:
             bool: True if the user instance was successfully deleted, False otherwise.
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None
        user.is_active = False
        user.deleted_at = datetime.now(UTC)
        return user