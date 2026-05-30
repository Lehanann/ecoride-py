from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.car_schema import CarCreate, CarRead
from app.services.car_service import CarService
from app.repositories.car_repository import CarRepository
from databases.postgresql import get_session

router = APIRouter(prefix="/cars", tags=["cars"])

# Dependency that provides a CarService instance with a database session
def get_service_car(db: AsyncSession = Depends(get_session)) -> CarService:
    return CarService(CarRepository(db))

@router.get("/", response_model=list[CarRead])
async def get_all_cars(request: Request, service: CarService = Depends(get_service_car)):
    """
    Retrieves a list of all cars for a user.

    This endpoint fetches all cars associated with a user stored in the database and returns
    them in the format specified by the CarRead schema.

    Args:
        request (Request): Request containing the user identifier allowed by the middleware auth.
            we can retrieve the identifier of the user.
        service (CarService): The service layer for handling user-related operations.
            This is injected automatically using Depends(get_service_car).

    Returns:
        list[CarRead]: List of all cars for the user, represented by the 'CarRead' schema which
        includes relevant car details such as ID.
    """
    user_id = request.state.user_id
    return await service.get_all_cars_by_user(user_id)

@router.post("/", response_model=dict[str,str], status_code=status.HTTP_201_CREATED)
async def create_car(request: Request, data: CarCreate, service: CarService = Depends(get_service_car)):
    """
    Creates a new car for a user from database.
    Args:
        request (Request): Request containing the user identifier allowed by the middleware auth.
            we can retrieve the identifier of the user.
        data (CarCreate): Schema containing all data required to create the car.
        service (CarService): The service layer for handling user-related operations.
            This is injected automatically using Depends(get_service_car).

    Returns:
        dict[str,str]: Message indicates the success of the creation of the car.
    """
    user_id = request.state.user_id
    await service.create(data, user_id)
    return {"message": "Car created successfully"}

@router.delete("/{car_id}",response_model=dict[str,str], status_code=status.HTTP_200_OK)
async def delete_car(request: Request, car_id: int, service: CarService = Depends(get_service_car)):
    """
    Deletes a car associated with a user from database.

    Args:
        request (Request): Request containing the user identifier allowed by the middleware auth.
            we can retrieve the identifier of the user.
        car_id (int): The unique identifier of the car to be deleted.
        service (CarService): The service layer for handling user-related operations.
            This is injected automatically using Depends(get_service_car).

    Returns:
        dict[str,str]: Message indicates the success of the deletion of the car.
    """
    user_id = request.state.user_id
    await service.delete(car_id, user_id)
    return {"message": "Car deleted successfully"}

