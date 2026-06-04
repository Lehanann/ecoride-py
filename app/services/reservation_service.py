import logging
from sqlalchemy.exc import IntegrityError
from app.core.exceptions.http_exceptions import bad_request, forbidden, not_found, conflict
from app.models.tables.reservation import Reservation
from app.repositories.carpooling_repository import CarpoolingRepository
from app.repositories.reservation_repository import ReservationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.reservation_schema import ReservationCreate
from app.utils.carpooling_status_enum import CarpoolingStatusEnum
from datetime import date

logger = logging.getLogger(__name__)

class ReservationService:
    """
    Service responsible for managing reservations.
    """

    USER_NOT_FOUND = "User not found"
    CARPOOLING_NOT_FOUND = "Carpooling not found"
    NOT_PASSENGER = "The user has not the 'passenger' role"
    RESERVATION_ALREADY_EXISTS = "Reservation already exists"
    RESERVATION_NOT_FOUND = "Reservation not found"
    PLACE_NOT_AVAILABLE = "Not enough place available"

    def __init__(self,
                 reservation_repository: ReservationRepository,
                 carpooling_repository: CarpoolingRepository,
                 user_repository: UserRepository) -> None:
        """
        Initialize the reservation service.

        Args:
            reservation_repository (ReservationRepository): The repository of the reservation.
            carpooling_repository (CarpoolingRepository): The repository of the carpooling.
            user_repository (UserRepository): The repository of the user.
        """
        self.reservation_repository = reservation_repository
        self.carpooling_repository = carpooling_repository
        self.user_repository = user_repository

    async def reserve(self, user_id: int, reservation_data: ReservationCreate) -> Reservation :
        """
        Reserve a place for a carpooling.

        Args:
            user_id (int): The unique identifier of the user to reserve.
            reservation_data (ReservationCreate): The schema reservation to reserve.

        Raises:
            not_found:
                - If the user is not found.
                - If the carpooling is not found.
            forbidden:
                - If the user has not the 'passenger' role.
            bad_request:
                - If an error occurs while reserving a carpooling.
            conflict:
                - If the reservation is already reserved.
                - if not enough place available.

        Returns:
            Reservation : The reservation of the carpooling.
        """
        # Retrieve and check user if exists
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise not_found(detail=self.USER_NOT_FOUND)

        # checks role user which contains passenger role
        roles = user.roles
        is_passenger = False
        for role in roles:
            if role.name == "passenger":
                is_passenger = True
                break
        if not is_passenger:
            raise forbidden(detail=self.NOT_PASSENGER)

        #check if carpooling exists, with published and date greater than today
        carpooling = await self.carpooling_repository.get_by_id(reservation_data.carpooling_id)
        if carpooling is None:
            raise not_found(detail=self.CARPOOLING_NOT_FOUND)
        if carpooling.status != CarpoolingStatusEnum.published:
            raise not_found(detail=self.CARPOOLING_NOT_FOUND)
        if carpooling.departure_date <= date.today():
            raise not_found(detail=self.CARPOOLING_NOT_FOUND)

        # checks if user already reserved this carpooling
        existing_reservation = await self.reservation_repository.get_reservation(user_id, reservation_data.carpooling_id)

        if existing_reservation is not None:
            raise conflict(detail=self.RESERVATION_ALREADY_EXISTS)

        # checks if place number is greater than 0
        if carpooling.place_number <= 0:
            raise conflict(detail=self.PLACE_NOT_AVAILABLE)

        # if not error, decrement place number
        try:
            # decrement a place
            carpooling.place_number -= 1
            # create reservation
            reservation_carpooling = await self.reservation_repository.create_reservation(user_id, reservation_data.carpooling_id)
            #commit the reservation
            await self.reservation_repository.db.commit()
            return reservation_carpooling
        except IntegrityError:
            await self.reservation_repository.db.rollback()
            logger.exception("Integrity error while reserving a carpooling")
            raise conflict(detail=self.RESERVATION_ALREADY_EXISTS)
        except Exception:
            await self.reservation_repository.db.rollback()
            logger.exception("Unexpected error while reserving a carpooling")
            raise bad_request(detail="Error creating reservation")

    async def cancel(self, user_id: int, carpooling_id: int) -> Reservation :
        """
        Cancel a reservation.

        Args:
            user_id (int): The unique identifier of the user to reserve.
            carpooling_id (int): The  unique identifier of the carpooling.

        Raises:
            not_found:
                - If the user is not found.
                - If the carpooling is not found.
                - If reservation not found.
            bad_request:
                - If an error occurs while cancelling a carpooling.
            conflict:
                - If a conflict occurs while cancelling the reservation

        Returns:
            Reservation : The reservation of the carpooling.
        """
        # checks if user exists
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise not_found(detail=self.USER_NOT_FOUND)

        # checks if carpooling exists, published and greater than today
        carpooling = await self.carpooling_repository.get_by_id(carpooling_id)
        if carpooling is None:
            raise not_found(detail=self.CARPOOLING_NOT_FOUND)
        if carpooling.status != CarpoolingStatusEnum.published:
            raise not_found(detail=self.CARPOOLING_NOT_FOUND)
        if carpooling.departure_date <= date.today():
            raise not_found(detail=self.CARPOOLING_NOT_FOUND)

        # checks if reservation exists
        user_reservation = await self.reservation_repository.get_reservation(user_id, carpooling_id)
        if user_reservation is None:
            raise not_found(detail=self.RESERVATION_NOT_FOUND)

        try:
            carpooling.place_number += 1
            await self.reservation_repository.delete_reservation(user_id, carpooling_id)
            await self.reservation_repository.db.commit()
            return user_reservation
        except IntegrityError:
            await self.reservation_repository.db.rollback()
            logger.exception("Integrity error while cancelling a reservation")
            raise conflict(detail=self.RESERVATION_ALREADY_EXISTS)
        except Exception:
            await self.reservation_repository.db.rollback()
            logger.exception("Unexpected error while cancelling a reservation")
            raise bad_request(detail="Error cancelling a reservation")

