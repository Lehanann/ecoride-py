from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tables.reservation import Reservation

class ReservationRepository:
    """
    Repository handling database operations related to the Reservation model.
    """
    def __init__(self, db: AsyncSession):
        """
        Initialize the ReservationRepository class.

        Args:
            db (AsyncSession): Asynchronous database session.
        """
        self.db = db

    async def get_reservation(self, user_id: int, carpooling_id: int) -> Reservation | None:
        """
        Retrieve a reservation by user and carpooling.

        Args:
            user_id (int): The unique identifier of the user.
            carpooling_id (int): The unique identifier of the carpooling.

        Returns:
            Reservation | None: The reservation instance if found, otherwise None.
        """
        return await self.db.scalar(select(Reservation).where(
                            Reservation.carpooling_id == carpooling_id,
                                        Reservation.user_id == user_id)
                                    )

    async def create_reservation(self, user_id: int, carpooling_id: int) -> Reservation:
        """
        Create a new reservation instance.

        Args:
            user_id (int): The unique identifier of the user.
            carpooling_id (int): The unique identifier of the carpooling.

        Returns:
            Reservation: The new reservation instance.
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
            user_id (int): The unique identifier of the user.
            carpooling_id (int): The unique identifier of the carpooling.

        Returns:
            Reservation | None: The reservation instance if found, otherwise None.
        """
        reservation = await self.get_reservation(user_id, carpooling_id)

        if reservation is None:
            return None

        await self.db.delete(reservation)
        return reservation



        


