from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tables.car import Car
from app.models.tables.user import User


class CarRepository:
    """
    Car repository providing CRUD operations for a given SQLAlchemy model.
    """
    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the Car repository with database session.
        Args:
            db (AsyncSession): Asynchronous database session.
        """
        self.db = db

    async def get_by_id(self, car_id: int) -> Car | None:
        """
        Retrieves a car by its ID.
        Args:
            car_id (int): The ID of the car to retrieve.
        Returns:
            Car | None: The car instance if found, otherwise None.
        """
        return await self.db.get(Car, car_id)

    async def get_all(self) -> list[Car]:
        """
        Retrieves all instances of car from database.
        Returns:

        """
        return list(await self.db.scalars(select(Car)))

    async def get_all_cars_by_user(self, user_id: int) -> list[Car] | None:
        """
        Retrieves all instances of car by their user ID.
        Args:
            user_id:

        Returns:

        """
        return list(await self.db.scalars(select(Car).where(User.id == user_id)))

    async def create(self, data: dict) -> Car:
        """
        Creates a new car instance.
        Args:
            data (dict): Schema containing fields to create the car instance.

        Returns:
            car (Car): The new car instance.
        """
        car = Car(**data)
        self.db.add(car)
        await self.db.commit()
        await self.db.refresh(car)
        return car

    async def update(self, car_id: int, data: dict) -> Car | None:
        """
        Updates a car by its ID.
        Args:
            car_id (int): The ID of the car to update.
            data (dict): The updated car instance.

        Returns:
            Car | None: The car instance if found, otherwise None.
        """
        car = await self.get_by_id(car_id)
        if car is None:
            return None

        for key, value in data.items():
            setattr(car, key, value)

        await self.db.commit()
        await self.db.refresh(car)

        return car

    async def delete(self, car_id: int) -> bool:
        """
        Deletes a car by its ID.
        Args:
            car_id (int): The ID of the car to delete.

        Returns:
            True if the car was successfully deleted, False otherwise.
        """
        car = await self.get_by_id(car_id)
        if car is None:
            return False

        await self.db.delete(car)
        await self.db.commit()
        return True
