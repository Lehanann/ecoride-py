from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.tables.user import User
from datetime import datetime, UTC

from app.models.tables.role import Role


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
            user_id: The unique identifier of the user.

        Returns:
            User | None: The user instance if found, otherwise None.
        """
        result = await self.db.execute(
            select(User)
            .where(
                User.id == user_id,
                User.is_active.is_(True)))
        return result.scalars().one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """
        Retrieve a user instance by its email.

        Args:
            email (str): the email of user.

        Returns:
             User | None: The user instance if found, otherwise None.
        """
        result = await self.db.execute(select(User).where(User.email == email,
                                                          User.is_active.is_(True))
                                       )
        return result.scalars().one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """
        Retrieve a user instance by its username.

        Args:
            username (str): The username of user.

        Returns:
             User | None: The user instance if found, otherwise None.
        """
        result = await self.db.execute(select(User).where(User.username == username,
                                                          User.is_active.is_(True))
                                       )
        return result.scalars().one_or_none()

    async def get_all(self) -> list[User]:
        """
        Retrieve all instances of user from the database.

        Returns:
            list[User]: The List of all user's instances.
        """
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.is_active.is_(True))
        )
        users = result.scalars().all()
        return users

    async def create(self, data: dict) -> User:
        """
        Create a new user instance, with the password hashed

        Args:
            data (dict): Schema containing fields to create the user instance.

        Returns:
             user(User): The newly created user instance.
        """
        user = User(**data)
        self.db.add(user)
        return user

    async def update(self,user_id: int, data: dict) -> User | None:
        """
        Update an existing user instance by its ID.

        Args
            user_id(int): The user ID to update.
            data (dict): Fields to update the user instance.

        Returns:
             user(User): The updated user instance.
        """
        user = await self.get_by_id(user_id)
        if user is None:
            return None

        for key, value in data.items():
            setattr(user, key, value)

        return user

    async def delete(self, user_id: int) -> User | None:
        """
        Delete an existing user instance by its ID.

        Args:
            user_id(int): The user ID to delete.

        Returns:
             User | None: The deleted user instance. otherwise None.
        """
        user = await self.get_by_id(user_id)
        if user is None:
            return None
        user.is_active = False
        user.deleted_at = datetime.now(UTC)
        return user

    async def count_admin_user(self):
        """
        Count the number of admin users in the database.
        Returns:
            int: The number of admin users in the database.
        """
        return await self.db.scalar(select(func.count(User.id)).filter(User.roles.any(Role.name == "administrator")))

    async def get_user_with_roles(self, user_id: int) -> User | None:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.roles))
            .where(User.id == user_id,
                   User.is_active.is_(True)
                   )
        )
        return result.scalars().one_or_none()

    async def get_user_with_roles_and_cars(self, user_id: int) -> User | None:
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.roles),
                     selectinload(User.cars))
            .where(User.id == user_id,
                   User.is_active.is_(True))
        )

        return result.scalars().one_or_none()

