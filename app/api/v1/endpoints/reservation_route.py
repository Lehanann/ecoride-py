from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.reservation_repository import ReservationRepository
from repositories.carpooling_repository import CarpoolingRepository
from repositories.user_repository import UserRepository
from app.services.reservation_service import ReservationService
from app.schemas.reservation_schema import ReservationCreate
from databases.postgresql import get_session


router = APIRouter()

def get_reservation_service( db: AsyncSession = Depends(get_session)) -> ReservationService:
    return ReservationService(ReservationRepository(db), CarpoolingRepository(db), UserRepository(db))


@router.post("/reservation", response_model=dict[str,str])
async def reserve(request: Request, reservation: ReservationCreate, service: ReservationService = Depends(get_reservation_service)):
    user_id = request.state.user_id
    await service.reserve(user_id, reservation)
    return {"message": "Reservation created"}

@router.delete("/reservation/{carpooling_id}", response_model=dict[str,str])
async def cancel(request: Request, carpooling_id: int, service: ReservationService = Depends(get_reservation_service)):
    user_id = request.state.user_id
    await service.cancel(user_id, carpooling_id)
    return {"message": "Reservation cancelled"}

