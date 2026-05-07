from fastapi import HTTPException
from app.models.tables.car import Car
from app.repositories.car_repository import CarRepository
from app.schemas.car_schema import CarCreate


class CarService:

    def __init__(self, repository: CarRepository) -> None:
        self.repository = repository

    async def get_all_cars_by_user(self, user_id: int) -> list[Car]:
        """
        Get all cars by user
        Args:
            user_id: User ID
        Returns:
            list[Car]: List of cars by user
        """
        return await self.repository.get_all_cars_by_user(user_id)

    async def create(self, data: CarCreate, user_id) -> Car:
        """
        Create a new car for a user
        Args:
            data (CarCreate): Car to be created
            user_id (int): User ID
        Returns:
            Car: New car instance
        """
        dataform = {
            "model" : data.model,
            "registration" : data.registration,
            "first_date_registration": data.first_date_registration,
            "energy": data.energy,
            "color": data.color,
            "brand_id": data.brand_id,
            "user_id": user_id,
        }

        try:
            return await self.repository.create(dataform)
        except Exception:
            raise HTTPException(status_code=400,detail="Error creating car")


    async def delete(self, car_id: int, user_id) -> None:

        car_exists = await self.repository.get_by_id(car_id)
        if not car_exists:
            raise HTTPException(status_code=404, detail="Car not found")
        if car_exists.user_id != user_id:
            raise HTTPException(status_code=403, detail="Failed to delete car")
        await self.repository.delete(car_id)
