from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.schemas.carpooling_schema import CarpoolingCreate, CarpoolingRead, CarpoolingUpdate, CarpoolingStatusUpdate
from app.services.carpooling_service import CarpoolingService
from app.repositories.carpooling_repository import CarpoolingRepository
from databases.postgresql import get_session
from app.services.transaction_service import TransactionService
from repositories.transaction_repository import TransactionRepository

router = APIRouter(prefix="/carpooling", tags=["carpooling"])

def get_service_carpooling(db: AsyncSession = Depends(get_session)) -> CarpoolingService:
    return CarpoolingService(CarpoolingRepository(db),
                             UserRepository(db),
                             TransactionService(
                                 TransactionRepository(db),
                                 CarpoolingRepository(db),
                                 UserRepository(db)))


@router.get("/", response_model=list[CarpoolingRead])
async def get_all_carpoolings(service: CarpoolingService = Depends(get_service_carpooling)):
    return await service.get_all_carpoolings()

@router.get("/{carpooling_id}", response_model=CarpoolingRead)
async def get_public_carpooling(carpooling_id: int, service: CarpoolingService = Depends(get_service_carpooling)):
    return await service .get_public_carpooling_by_id(carpooling_id)

@router.post("/", response_model=dict[str,str], status_code=status.HTTP_201_CREATED)
async def create_carpooling(request: Request,
                            data: CarpoolingCreate,
                            service: CarpoolingService = Depends(get_service_carpooling)):

    user_id = request.state.user_id
    await service.create_carpooling(data, user_id)
    return {"message": "Carpooling was created"}

@router.patch("/{carpooling_id}", response_model=CarpoolingRead, status_code=status.HTTP_200_OK)
async def update_carpooling(request: Request,
                            carpooling_id: int,
                            data: CarpoolingUpdate,
                            service: CarpoolingService = Depends(get_service_carpooling)):

    user_id = request.state.user_id

    return await service.update_carpooling(carpooling_id, data, user_id)

@router.patch("/{carpooling_id}/status", response_model=CarpoolingRead, status_code=status.HTTP_200_OK)
async def update_carpooling_status(request: Request,
                                   carpooling_id: int,
                                   data: CarpoolingStatusUpdate,
                                   service: CarpoolingService = Depends(get_service_carpooling)):

    user_id = request.state.user_id
    return await service.update_status_carpooling(carpooling_id, data, user_id)