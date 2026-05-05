from fastapi import HTTPException

from app.models.tables.car import Car
from app.repositories.car_repository import CarRepository
from app.schemas.car_schema import CarCreate, CarUpdate


class CarService:

    def __init__(self, repository: CarRepository) -> None:
        self.repository = repository

    async def get_by_id(self, car_id: int) -> Car:

        car = await self.repository.get_by_id(car_id)
        if not car:
            raise HTTPException(status_code=404,detail="Car not found")
        return car

    async def get_all(self) -> list[Car]:
        return await self.repository.get_all()

    async def create(self, data: CarCreate) -> Car:

        dataform = {
            "model" : data.model,
            "registration" : data.registration,
            "first_date_registration": data.first_date_registration,
            "energy": data.energy,
            "color": data.color,
            "brand_id": data.brand_id,
            "user_id": data.user_id,
        }

        try:
            return await self.repository.create(dataform)
        except Exception:
            raise HTTPException(status_code=400,detail="Error creating car")

    async def update(self, car_id: int, data: CarUpdate) -> Car:

        dataform = data.model_dump(exclude_unset=True)

        try:
            updated_car = await self.repository.update(car_id, dataform)
            if updated_car is None:
                raise HTTPException(status_code=404,detail="Car not found")
            return updated_car
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=400,detail="Error updating car")