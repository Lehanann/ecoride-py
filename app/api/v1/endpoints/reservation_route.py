from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.reservation_repository import ReservationRepository
from app.repositories.carpooling_repository import CarpoolingRepository
from app.repositories.user_repository import UserRepository
from app.services.reservation_service import ReservationService
from app.schemas.reservation_schema import ReservationCreate
from databases.postgresql import get_session


router = APIRouter(prefix="/reservations", tags=["reservations"])

def get_service_reservation( db: AsyncSession = Depends(get_session)) -> ReservationService:
    """
    Provide an instance of ReservationService with injected repositories.
    """
    return ReservationService(ReservationRepository(db), CarpoolingRepository(db), UserRepository(db))


@router.post("/", response_model=dict[str,str])
async def reserve(request: Request, reservation: ReservationCreate, service: ReservationService = Depends(get_service_reservation)):
    """
    Reserve a place seat of a carpooling.

    Args:
        request (Request): Request containing the user identifier allowed by the middleware auth.
            we can retrieve the identifier of the user.
        reservation (ReservationCreate): Schema containing all data required to create the reservation
        service (ReservationService): The service layer for handling user-related operations.
            This is injected automatically using Depends(get_service_reservation).

    Returns:
        dict[str,str]: Message creating a reservation successfully.
    """
    user_id = request.state.user_id
    await service.reserve(user_id, reservation)
    return {"message": "Reservation created"}

@router.delete("/{carpooling_id}", response_model=dict[str, str])
async def cancel(request: Request, carpooling_id: int, service: ReservationService = Depends(get_service_reservation)):
    """
        Cancel a place seat for a carpooling.

        Args:
            request (Request): Request containing the user identifier allowed by the middleware auth.
                we can retrieve the identifier of the user.
            carpooling_id (int): The unique identifier of the carpooling.
            service (ReservationService): The service layer for handling user-related operations.
                This is injected automatically using Depends(get_service_reservation).

        Returns:
            dict[str,str]: Message cancelling a reservation successfully.
        """
    user_id = request.state.user_id
    await service.cancel(user_id, carpooling_id)
    return {"message": "Reservation cancelled"}

