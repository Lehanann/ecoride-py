from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tables.opinion import Opinion
from app.utils.opinion_status_enum import OpinionStatusEnum
from datetime import datetime

class OpinionRepository:
    """
    Repository handling database operations related to the Opinion model
    """
    def __init__(self, db: AsyncSession) -> None:
        """
        Initialize the OpinionRepository class.

        Args:
            db (AsyncSession): Asynchronous database session.
        """
        self.db = db

    async def get_by_id(self, opinion_id: int) -> Opinion | None:
        """
        Retrieve an opinion by its ID.
        Args:
            opinion_id (int): The opinion ID.

        Returns:
            Opinion | None: The opinion if found, otherwise None.
        """
        return await self.db.get(Opinion, opinion_id)

    async def get_all_by_status_pending(self) -> list[Opinion]:
        """
        Retrieve all opinions with a pending status.

        Returns:
            list[Opinion]: The list of pending opinions.
        """
        return list(await self.db.scalars(select(Opinion).where(Opinion.status == OpinionStatusEnum.pending)))

    async def get_all_by_status_rejected(self) -> list[Opinion]:
        """
        Retrieve all opinions with a rejected status.

        Returns:
            list[Opinion]: The list of rejected opinions.
        """
        return list(await self.db.scalars(select(Opinion).where(Opinion.status == OpinionStatusEnum.rejected)))

    async def get_all_by_user(self, user_id: int) -> list[Opinion]:
        """
        Retrieve all approved opinions received by a given user.
        Args:
            user_id (int): identifier of the target user.

        Returns:
            list[Opinion]: The list approved opinions for the user.
        """
        return list(await self.db.scalars(select(Opinion)
                                          .where(Opinion.target_id == user_id)
                                          .where(Opinion.status == OpinionStatusEnum.approved)))

    async def create(self, data: dict) -> Opinion:
        """
        Create a new opinion.

        Args:
            data (dict): Data used to create the new opinion.

        Returns:
            Opinion: The created opinion instance.
        """
        opinion = Opinion(**data)
        self.db.add(opinion)
        return opinion

    async def update_status(self,
                            opinion_id: int,
                            status: OpinionStatusEnum,
                            validator_id: int,
                            validated_at: datetime
                            ) -> Opinion | None:
        """
        Update the status of an opinion after validation.
        Args:
            opinion_id (int): Identifier of the opinion.
            status (OpinionStatusEnum): New status (approved or rejected).
            validator_id (int): Identifier of the employee validating the opinion.
            validated_at (datetime): Timestamp of the validation.

        Returns:
            Opinion | None: The updated opinion if found, otherwise None.
        """
        opinion = await self.get_by_id(opinion_id)
        if opinion is None:
            return None
        opinion.status = status
        opinion.validator_id = validator_id
        opinion.validated_at = validated_at
        return opinion
