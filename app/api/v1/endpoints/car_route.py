from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.car_schema import CarRead, CarCreate, CarUpdate
from app.services.car_service import CarService
from app.repositories.car_repository import CarRepository
from databases.postgresql import get_session

router = APIRouter(prefix="/car", tags=["car"])

def get_service_car(db: AsyncSession = Depends(get_session)) -> CarService:
    return CarService(CarRepository(db))

@router.get("/", response_model=list[CarRead])
async def list_cars(service: CarService = Depends(get_session)):
    return await service.get_all()

@router.get("/{car_id}", response_model=CarRead)
async def get_car(car_id: int, service: CarService = Depends(get_session)):
    return await service.get_by_id(car_id)

@router.post("/", response_model=dict[str,str], status_code=status.HTTP_201_CREATED)
async def create_car(data: CarCreate, service: CarService = Depends(get_session)):
    await service.create(data)
    return {"message": "car created successfully"}

@router.patch("/{car_id}", response_model=dict[str,str], status_code=status.HTTP_200_OK)
async def update_car(car_id: int , data: CarUpdate, service: CarService = Depends(get_session)):
    await service.update(car_id, data)
    return {"message": "car updated successfully"}