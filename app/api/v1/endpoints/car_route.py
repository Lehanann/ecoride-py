from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.car_schema import CarCreate, CarRead
from app.services.car_service import CarService
from app.repositories.car_repository import CarRepository
from databases.postgresql import get_session

router = APIRouter(prefix="/car", tags=["car"])

def get_service_car(db: AsyncSession = Depends(get_session)) -> CarService:
    return CarService(CarRepository(db))


@router.get("/", response_model=list[CarRead])
async def get_all_cars(request: Request, service: CarService = Depends(get_service_car)):
    """

    Args:
        request:
        service:

    Returns:

    """
    user_id = request.state.user_id
    return await service.get_all_cars_by_user(user_id)

@router.post("/", response_model=dict[str,str], status_code=status.HTTP_201_CREATED)
async def create_car(request: Request, data: CarCreate, service: CarService = Depends(get_service_car)):
    user_id = request.state.user_id
    await service.create(data, user_id)
    return {"message": "car created successfully"}

@router.delete("/{car_id}",response_model=dict[str,str], status_code=status.HTTP_200_OK)
async def delete_car(request: Request, car_id: int, service: CarService = Depends(get_service_car)):
    user_id = request.state.user_id
    await service.delete(car_id, user_id)
    return {"message": "car deleted successfully"}

