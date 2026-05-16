from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tables.reservation import Reservation

class ReservationRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_reservation(self, user_id: int, carpooling_id: int) -> Reservation | None:
        """
        Retrieve a reservation by carpooling_id and user_id.
        Args:
            carpooling_id (int): Carpooling ID.
            user_id (int): User ID.

        Returns:
            Reservation | None: Reservation instance if found, otherwise None.
        """
        return await self.db.scalar(select(Reservation).
                                    where(Reservation.carpooling_id == carpooling_id, Reservation.user_id == user_id))

    async def create_reservation(self, user_id: int, carpooling_id: int) -> Reservation:
        """
        Create a new reservation.
        Args:
            user_id:
            carpooling_id:

        Returns:

        """
        reservation = Reservation()
        reservation.user_id = user_id
        reservation.carpooling_id = carpooling_id
        self.db.add(reservation)
        return reservation


    async def delete_reservation(self, user_id: int, carpooling_id: int) -> Reservation | None:
        """
        Delete an existing reservation.
        Args:
            user_id:
            carpooling_id:

        Returns:

        """
        reservation = await self.get_reservation(user_id,carpooling_id)

        if reservation is None:
            return None

        await self.db.delete(reservation)

        return reservation



        


