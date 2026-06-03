import logging
from sqlalchemy.exc import IntegrityError
from app.core.exceptions.http_exceptions import bad_request, forbidden, not_found, conflict
from app.models.tables.car import Car
from app.repositories.car_repository import CarRepository
from app.schemas.car_schema import CarCreate

logger = logging.getLogger(__name__)

class CarService:
    """
    Car service that performs operations on the car repository such as reading, creating, and deleting cars.
    """
    CAR_NOT_FOUND = "Car not found"
    NOT_ALLOWED_DELETE = "You are not allowed to delete this car"
    CAR_ALREADY_EXISTS = "Car already exists"

    def __init__(self, repository: CarRepository) -> None:
        """
        Initialize the Car service with the car repository.

        Args:
            repository (CarRepository): The repository of the car.
        """
        self.repository = repository

    async def get_all_cars_by_user(self, user_id: int) -> list[Car]:
        """
        Retrieve all cars associated with a user.

        Args:
            user_id (int): The unique identifier of the user.

        Returns:
            list[Car]: List of cars associated with the user.
        """
        return await self.repository.get_all_cars_by_user(user_id)

    async def create(self, data: CarCreate, user_id: int) -> Car:
        """
        Create a new car for a specific user.

        Args:
            data (CarCreate): The data required to create a Car.
            user_id (int): The unique identifier of the user.

        Raises:
            bad_request:
                - If an error occurs while creating a car.
            conflict:
                - if the car already exists.

        Returns:
            Car: The newly created car.
        """
        car_data = {
            "model": data.model,
            "registration" : data.registration,
            "first_registration_date": data.first_registration_date,
            "energy": data.energy,
            "color": data.color,
            "brand_id": data.brand_id,
            "user_id": user_id,
        }

        try:
            new_car = await self.repository.create(car_data)
            await self.repository.db.commit()
            return new_car
        except IntegrityError:
            await self.repository.db.rollback()
            logger.exception("Integrity error while creating car")
            raise conflict(detail=self.CAR_ALREADY_EXISTS)
        except Exception:
            await self.repository.db.rollback()
            logger.exception("Unexpected error while creating a car")
            raise bad_request(detail="Error creating car")


    async def delete(self, car_id: int, user_id: int) -> Car:
        """
        Delete a car owned by the user.

        Args:
            car_id (int): The unique identifier of the car.
            user_id (int): The unique identifier of the user.

        Raises:
            not_found:
                - If the car is not found.
            forbidden:
                - If the car does not belong to the user.
            bad_request:
                - If an error occurs while deleting a car.

        Returns:
            Car: The deleted car.
        """
        deleted_car = await self.repository.get_by_id(car_id)

        if deleted_car is None:
            raise not_found(detail=self.CAR_NOT_FOUND)

        if deleted_car.user_id != user_id:
            raise forbidden(detail=self.NOT_ALLOWED_DELETE)

        try:
            await self.repository.delete(car_id)
            await self.repository.db.commit()
            return deleted_car
        except Exception:
            await self.repository.db.rollback()
            logger.exception("Unexpected error while deleting car")
            raise bad_request(detail="Error deleting car")