from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tables.carpooling import Carpooling
from app.models.tables.car import Car
from app.utils.carpooling_status_enum import CarpoolingStatusEnum


class CarpoolingRepository:
    """
    Carpooling repository providing CRUD operations for a given SQLAlchemy model.

    """
    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the Carpooling repository with database session.

        Args:
            db (AsyncSession): Asynchronous database session.
        """
        self.db = db

    async def get_by_id(self, carpooling_id: int) -> Carpooling | None:
        """
        Retrieve a carpooling by its id.

        Args:
            carpooling_id:

        Returns:
            Carpooling | None: The carpooling instance if found, otherwise None.
        """
        return await self.db.get(Carpooling, carpooling_id)

    async def get_all(self) -> list[Carpooling]:
        """
        Retrieve all instances of carpooling from the database.

        Returns:
            list[Carpooling]: The List of all carpooling's instances.
        """
        return list(await self.db.scalars(select(Carpooling)))


    async def get_all_carpoolings_by_user(self, user_id: int) -> list[Carpooling]:
        """
        Retrieve all carpoolings by a user.

        Args:
            user_id (int): The ID of user.

        Returns:
            list[Carpooling]: The list of all carpooling's instances.
        """
        return list(await self.db.scalars(select(Carpooling).join(Carpooling.car).filter(Car.user_id == user_id)))

    async def create(self, data: dict) -> Carpooling:
        """
        Create a new carpooling instance.

        Args:
            data (dict): Schema containing fields to create the new carpooling instance.

        Returns:
            Carpooling: The new carpooling instance.
        """
        carpooling = Carpooling(**data)
        self.db.add(carpooling)
        await self.db.commit()
        await self.db.refresh(carpooling)
        return carpooling

    async def update(self, carpooling_id: int, data: dict ) -> Carpooling | None:
        """
        Update a carpooling instance.

        Args:
            carpooling_id (int): The ID of carpooling instance.
            data (dict): Schema containing fields to update the new carpooling instance.

        Returns:
            Carpooling: The updated carpooling instance

        Side Effects:
            Commits changes to the database and refreshes the carpooling instance.
        """
        carpooling = await self.get_by_id(carpooling_id)

        if carpooling is None:
            return None

        for key, value in data.items():
            setattr(carpooling, key, value)

        await self.db.commit()
        await self.db.refresh(carpooling)
        return carpooling

    async def update_status(self, carpooling_id: int, status: CarpoolingStatusEnum) -> Carpooling | None:
        """
        Update the status of a carpooling.

        Args:
            carpooling_id (int): The ID of carpooling instance.
            status (CarpoolingStatusEnum): Containing field to update only status of the carpooling.

        Returns:
            Carpooling: The updated carpooling instance.

        Side Effects:
            Commits changes to the database and refreshes only the status carpooling.
        """
        carpooling = await self.get_by_id(carpooling_id)

        if carpooling is None:
            return None

        carpooling.status = status
        await self.db.commit()
        await self.db.refresh(carpooling)
        return carpooling

    async def delete(self, carpooling_id: int) -> bool:
        """
        Delete an existing carpooling instance by its ID.

        Args:
            carpooling_id(int): The carpooling ID to delete.

        Returns:
             bool: True if the carpooling instance was successfully deleted, False otherwise.

        Side Effects:
            Commits deletion to the database.
        """
        carpooling = await self.get_by_id(carpooling_id)
        if carpooling is None:
            return False
        await self.db.delete(carpooling)
        await self.db.commit()
        return True