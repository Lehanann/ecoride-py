from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.repositories.opinion_repository import OpinionRepository
from psycopg import IntegrityError
from app.repositories.user_repository import UserRepository
from app.repositories.carpooling_repository import CarpoolingRepository
from app.models.tables.opinion import Opinion
from schemas.opinion_schema import OpinionCreate, OpinionStatusUpdate
from app.utils.opinion_status_enum import OpinionStatusEnum
from app.utils.carpooling_status_enum import CarpoolingStatusEnum

class OpinionService:
    """
    Service handling business logic related to opinions.
    Includes creation, validation, and retrieval workflows.
    """
    def __init__(self, opinion_repository: OpinionRepository, user_repository: UserRepository, carpooling_repository: CarpoolingRepository):
        """
        Initialize the service with required repositories.
        Args:
            opinion_repository (OpinionRepository): Repository for opinion data.
            user_repository (UserRepository): Repository for user data.
            carpooling_repository (CarpoolingRepository): Repository for carpooling data.
        """
        self.opinion_repository = opinion_repository
        self.user_repository = user_repository
        self.carpooling_repository = carpooling_repository

    async def get_pending_opinions(self) -> list[Opinion]:
        """
        Retrieve all opinions awaiting validation.

        Returns:
             list[Opinion]: List of pending opinions.
        """
        return await self.opinion_repository.get_all_by_status_pending()

    async def get_opinions_for_driver(self, user_id: int) -> list[Opinion]:
        """
        Retrieve all approved opinions received by a driver.
        Args:
            user_id (int): Identifier of the driver.

        Returns:
            list[Opinion]: List of approved opinions for the driver.

        Raises:
            HTTPException: If the user does not exist.
        """
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return await self.opinion_repository.get_all_by_user(user_id)

    async def create_opinion(self, author_id: int, opinion: OpinionCreate) -> Opinion:
        """
        Create a new opinion for a completed carpooling.

        Validates:
        - Author existence
        - Carpooling existence and completion status
        - Prevents self-review
        - Ensures the author participated in the carpooling

        Args:
            author_id (int): Identifier of the opinion author (passenger).
            opinion (OpinionCreate): Data used to create the opinion.

        Returns:
            Opinion: The created opinion.

        Raises:
            HTTPException: If validation fails or a database error occurs.
        """
        author = await self.user_repository.get_by_id(author_id)
        if author is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Author not found")

        carpooling = await self.carpooling_repository.get_by_id(opinion.carpooling_id)
        if carpooling is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carpooling not found")
        if carpooling.status != CarpoolingStatusEnum.finished:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Carpooling not finished")

        target_id = carpooling.car.user_id

        if author_id == target_id:
            raise HTTPException(status_code=400, detail="You cannot review yourself")

        if author_id not in [p.user_id for p in carpooling.passengers]:
            raise HTTPException(status_code=403, detail="User not part of this carpooling")

        dataform = {
            "comment": opinion.comment,
            "note": opinion.note,
            "status": OpinionStatusEnum.pending,
            "carpooling_id": carpooling.id,
            "author_id": author_id,
            "target_id": target_id,
        }
        try:
            opinion = await self.opinion_repository.create(dataform)
            await self.opinion_repository.db.commit()
            return opinion
        except IntegrityError:
            await self.opinion_repository.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    async def validate_opinion(self, opinion_id: int, opinion: OpinionStatusUpdate, validator_id: int) -> Opinion:
        """
        Validate or reject an opinion.

        Only users with the employee role can perform this action.
        The opinion must exist and be in a pending state.

        Args:
            opinion_id (int): Identifier of the opinion.
            opinion (OpinionStatusUpdate): Data containing the new status.
            validator_id (int): Identifier of the employee validating the opinion.

        Returns:
            Opinion: The updated opinion.

        Raises:
            HTTPException:
                - 404 if user or opinion is not found
                - 403 if user is not authorized
                - 400 if opinion is not in pending state or update fails
        """
        validator = await self.user_repository.get_by_id(validator_id)

        if validator is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Checks that the user has the 'employee' role
        roles = validator.roles
        is_employee = False
        for role in roles:
            if role.name == "employee":
                is_employee = True
                break

        if not is_employee:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        # Checks current opinion exists
        current_opinion = await self.opinion_repository.get_by_id(opinion_id)
        if current_opinion is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opinion not found")

        # checks current opinion is pending status.
        if current_opinion.status != OpinionStatusEnum.pending:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Opinion not pending")

        try:
            updated_opinion = await self.opinion_repository.update_status(opinion_id,
                                                                          opinion.status,
                                                                          validator.id,
                                                                          validated_at=datetime.now(timezone.utc))
            if updated_opinion is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Opinion not updated")
            await self.opinion_repository.db.commit()
            return updated_opinion
        except IntegrityError:
            await self.opinion_repository.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    async def get_rejected_opinions(self) -> list[Opinion]:
        """
        Retrieve all rejected opinions.
        Returns:
            list[Opinion]: List of rejected opinions.
        """
        return await self.opinion_repository.get_all_by_status_rejected()
