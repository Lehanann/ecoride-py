from datetime import date, timedelta, datetime, time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from app.models.tables.carpooling import Carpooling
from app.models.tables.car import Car
from app.models.tables.reservation import Reservation
from app.utils.carpooling_status_enum import CarpoolingStatusEnum
from app.schemas.statistics_schema import CarpoolingStat



class CarpoolingRepository:
    """
    Carpooling repository providing CRUD operations for a given SQLAlchemy model.

    """
    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the Carpooling repository with database session.

        Args:
            db (AsyncSession): Asynchronous database session.
        """
        self.db = db

    async def get_by_id(self, carpooling_id: int) -> Carpooling | None:
        """
        Retrieve a carpooling by its ID, including its related car, reservations, and associated users.

        Args:
            carpooling_id (int): The unique identifier of the carpooling.

        Returns:
            Carpooling | None: The carpooling instance if found, otherwise None.
        """
        result = await self.db.execute(
            select(Carpooling)
            .options(
                selectinload(Carpooling.car).selectinload(Car.brand),
                selectinload(Carpooling.car).selectinload(Car.user),
                selectinload(Carpooling.reservations).selectinload(Reservation.user))
            .where(Carpooling.id == carpooling_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Carpooling]:
        """
        Retrieve all instances of carpooling.

        Returns:
            list[Carpooling]: The list of all carpooling instances.
        """
        return list(await self.db.scalars(select(Carpooling)))

    async def search_carpoolings(
        self,
        departure_location: str,
        end_location: str,
        ) -> list[Carpooling]:

            today = date.today()
            current_time = datetime.now().time()
            result = await self.db.scalars(
                select(Carpooling)
                .options(
                    selectinload(Carpooling.car).selectinload(Car.brand),
                    selectinload(Carpooling.car).selectinload(Car.user),
                )
                .where(
                    Carpooling.departure_location.ilike(f"%{departure_location}%"),
                    Carpooling.end_location.ilike(f"%{end_location}%"),
                    Carpooling.status == CarpoolingStatusEnum.published,
                    or_(
                        Carpooling.departure_date > today, and_(
                            Carpooling.departure_date == today,
                        Carpooling.departure_time >= current_time)
                    )
                )
                .order_by(
                    Carpooling.departure_date.asc(),
                    Carpooling.departure_time.asc(),
                )
            )

            return list(result)

    async def get_all_carpoolings_by_user(self, user_id: int) -> list[Carpooling]:
        """
        Retrieve all carpoolings by a user.

        Args:
            user_id (int): The unique identifier of user.

        Returns:
            list[Carpooling]: List of all carpoolings associated with the user.
        """
        return list(await self.db.scalars(
            select(Carpooling)
            .options(
                selectinload(Carpooling.car).selectinload(Car.brand),
                selectinload(Carpooling.car).selectinload(Car.user),
            )
            .join(Carpooling.car)
            .where(Car.user_id == user_id)))

    async def create(self, data: dict) -> Carpooling:
        """
        Create a new carpooling instance.

        Args:
            data (dict): Schema containing fields to create the new carpooling.

        Returns:
            Carpooling: The new carpooling instance.
        """
        carpooling = Carpooling(**data)
        self.db.add(carpooling)
        return carpooling

    async def update(self, carpooling_id: int, data: dict ) -> Carpooling | None:
        """
        Update a carpooling instance.

        Args:
            carpooling_id (int): The unique identifier of the carpooling.
            data (dict): Schema containing fields to update the carpooling.

        Returns:
            Carpooling | None: The updated carpooling instance if found, otherwise None.
        """
        carpooling = await self.get_by_id(carpooling_id)

        if carpooling is None:
            return None

        for key, value in data.items():
            setattr(carpooling, key, value)

        return carpooling

    async def update_status(self, carpooling_id: int, status: CarpoolingStatusEnum) -> Carpooling | None:
        """
        Update the status of a carpooling.

        Args:
            carpooling_id (int): The unique identifier of the carpooling.
            status (CarpoolingStatusEnum): The new status of the carpooling.

        Returns:
            Carpooling | None: The updated carpooling instance, otherwise None.
        """
        carpooling = await self.get_by_id(carpooling_id)

        if carpooling is None:
            return None

        carpooling.status = status
        return carpooling

    async def delete(self, carpooling_id: int) -> Carpooling | None:
        """
        Delete an existing carpooling instance by its ID.

        Args:
            carpooling_id (int): The unique identifier of the carpooling to delete.

        Returns:
             Carpooling | None: The deleted carpooling instance if found, otherwise None.
        """
        carpooling = await self.get_by_id(carpooling_id)
        if carpooling is None:
            return None
        await self.db.delete(carpooling)
        return carpooling

    async def get_carpooling_last_7_days(self) -> list[CarpoolingStat]:
        seven_days_ago = (
                date.today()
                - timedelta(days=7)
        )

        result = await self.db.execute(
            select(
                Carpooling.departure_date.label("date"),
                func.count(Carpooling.id).label("carpooling_count")
            )
            .where(
                Carpooling.departure_date >= seven_days_ago, )
            .group_by(Carpooling.departure_date)
            .order_by(Carpooling.departure_date)
        )

        rows = result.all()
        return [CarpoolingStat(
            date=row.date,
            count=row.carpooling_count,
        )
        for row in rows
        ]