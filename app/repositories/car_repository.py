from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tables.car import Car


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
        Retrieve a car instance by its ID.

        Args:
            car_id (int): The unique identifier of the car.

        Returns:
            Car | None: The car instance if found, otherwise None.

        """
        return await self.db.get(Car, car_id)


    async def get_all_cars_by_user(self, user_id: int) -> list[Car]:
        """
        Retrieves all instances of car by their user ID.

        Args:
            user_id (int): The unique identifier of the user.

        Returns:
            list[Car]: List of car instances by their user ID.
        """
        return list(await self.db.scalars(select(Car).where(Car.user_id == user_id)))

    async def create(self, data: dict) -> Car:
        """
        Creates a new car instance.

        Args:
            data (dict): Schema containing fields to create the car.

        Returns:
            Car: The new car instance.
        """
        car = Car(**data)
        self.db.add(car)
        return car

    async def delete(self, car_id: int) -> Car | None:
        """
        Deletes a car by its ID.

        Args:
            car_id (int): The unique identifier of the car.

        Returns:
            Car | None: The deleted car instance if found, otherwise None.
        """
        car = await self.get_by_id(car_id)
        if car is None:
            return None
        await self.db.delete(car)
        return car
