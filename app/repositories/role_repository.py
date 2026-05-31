from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tables.role import Role

class RoleRepository:
    """
    Role repository providing a method to retrieve roles.
    """
    def __init__(self, db: AsyncSession):
        """
        Initialize the Role repository with database session.

        Args:
            db (AsyncSession): Asynchronous database session.
        """
        self.db = db

    async def get_by_name(self, name: str) -> Role | None:
        """
        Retrieve a role by name.
        Args:
            name (str): The name of the role.

        Returns:
            Role | None: The role instance if found, otherwise None.
        """

        return await self.db.scalar(
            select(Role).where(Role.name == name)
        )