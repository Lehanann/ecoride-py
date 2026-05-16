from fastapi import HTTPException, status
from psycopg import IntegrityError
from app.models.tables.reservation import Reservation
from app.repositories.carpooling_repository import CarpoolingRepository
from app.repositories.reservation_repository import ReservationRepository
from app.repositories.user_repository import UserRepository
from app.schemas.reservation_schema import ReservationCreate
from app.utils.carpooling_status_enum import CarpoolingStatusEnum
from datetime import date

from models.tables import reservation


class ReservationService:

    def __init__(self,
                 reservation_repository: ReservationRepository,
                 carpooling_repository: CarpoolingRepository,
                 user_repository: UserRepository) -> None:
        """
        Constructor for the Reservation Service.
        Args:
            reservation_repository:
            carpooling_repository:
            user_repository:
        """
        self.reservation_repository = reservation_repository
        self.carpooling_repository = carpooling_repository
        self.user_repository = user_repository

    async def reserve(self, user_id: int, reservation: ReservationCreate) -> Reservation :
        """
        Reserve a place for a carpooling.
        Args:
            user_id (int): The ID of the user to reserve.
            reservation (ReservationCreate): The schema reservation to reserve.

        Returns:
            Reservation : The reservation of the carpooling.
        """
        # Retrieve and check user if exists
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        # checks role user which contains passenger role
        roles = user.roles
        is_passenger = False
        for role in roles:
            if role == "passenger":
                is_passenger = True
                break
        if not is_passenger:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        #check if carpooling exists, with published and date greater than today
        carpooling = await self.carpooling_repository.get_by_id(reservation.carpooling_id)
        if carpooling is None:
            raise HTTPException(status_code=404, detail="Carpooling not found")
        if carpooling.status != CarpoolingStatusEnum.published:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        if carpooling.departure_date <= date.today():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        # checks if user already reserved this carpooling
        existing_reservation = await self.reservation_repository.get_reservation(user_id, reservation.carpooling_id)

        if existing_reservation is not None:
            raise HTTPException(status_code=409, detail="Reservation already exists")

        # checks if place number is greater than 0
        if carpooling.place_number <= 0:
            raise HTTPException(status_code=409, detail="Not enough place available")

        # if not error, decrement place number
        try:
            # decrement a place
            carpooling.place_number -= 1
            # create reservation
            reservation_carpooling = await self.reservation_repository.create_reservation(user_id, reservation.carpooling_id)
            #commit the reservation
            await self.reservation_repository.db.commit()
            return reservation_carpooling
        except IntegrityError:
            # rollback reservation if
            await self.reservation_repository.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    async def cancel(self, user_id: int, carpooling_id: int) -> Reservation :
        # checks if user exists
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # checks if carpooling exists, published and greater than today
        carpooling = await self.carpooling_repository.get_by_id(carpooling_id)
        if carpooling is None:
            raise HTTPException(status_code=404, detail="Carpooling not found")
        if carpooling.status != CarpoolingStatusEnum.published:
            raise HTTPException(status_code=404, detail="Carpooling not found")
        if carpooling.departure_date <= date.today():
            raise HTTPException(status_code=404, detail="Carpooling not found")

        # checks if reservation exists
        user_reservation = await self.reservation_repository.get_reservation(user_id, carpooling_id)
        if user_reservation is None:
            raise HTTPException(status_code=404, detail="Reservation not found")

        try:
            carpooling.place_number += 1
            await self.reservation_repository.delete_reservation(user_id, carpooling_id)
            await self.reservation_repository.db.commit()
            return user_reservation
        except IntegrityError:
            await self.reservation_repository.db.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)

