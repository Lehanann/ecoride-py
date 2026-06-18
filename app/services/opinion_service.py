import logging
from sqlalchemy.exc import IntegrityError
from app.core.exceptions.http_exceptions import bad_request, forbidden, not_found, conflict
from datetime import datetime, timezone
from app.repositories.opinion_repository import OpinionRepository
from app.repositories.user_repository import UserRepository
from app.repositories.carpooling_repository import CarpoolingRepository
from app.models.tables.opinion import Opinion
from app.schemas.opinion_schema import OpinionCreate, OpinionStatusUpdate
from app.utils.opinion_status_enum import OpinionStatusEnum
from app.utils.carpooling_status_enum import CarpoolingStatusEnum

logger = logging.getLogger(__name__)

class OpinionService:
    """
    Service handling business logic related to opinions.
    Includes creation, validation, and retrieval workflows.
    """
    USER_NOT_FOUND = "User not found"
    CARPOOLING_NOT_FOUND = "Carpooling not found"
    OPINION_NOT_FOUND = "Opinion not found"
    OPINION_ALREADY_EXISTS = "Opinion already exists"
    CARPOOLING_NOT_FINISHED = "Carpooling not finished"
    NOT_EMPLOYEE = "User has not the 'employee' role"
    OPINION_NOT_PENDING = "Opinion not pending"
    OPINION_NOT_UPDATED = "Opinion not updated"
    USER_NOT_PARTICIPANT = "User is not part of this carpooling"

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
            user_id (int): The unique identifier of the driver.

        Raises:
            not_found:
                - If the user does not exist.

        Returns:
            list[Opinion]: List of approved opinions for the driver.
        """
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise not_found(detail=self.USER_NOT_FOUND)

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
            author_id (int): The unique identifier of the opinion author (passenger).
            opinion (OpinionCreate): The data used to create the opinion.

        Raises:
            not_found:
                - If the user is not found.
                - If the carpooling is not found.
            forbidden:
                - If the user does not part of this carpooling.
            bad_request:
                - If the carpooling is not finished.
                - If an error occurs while creating the opinion.

        Returns:
            Opinion: The created opinion.
        """
        author = await self.user_repository.get_by_id(author_id)
        if author is None:
            raise not_found(detail=self.USER_NOT_FOUND)

        carpooling = await self.carpooling_repository.get_by_id(opinion.carpooling_id)
        if carpooling is None:
            raise not_found(detail=self.CARPOOLING_NOT_FOUND)
        if carpooling.status != CarpoolingStatusEnum.finished:
            raise bad_request(detail=self.CARPOOLING_NOT_FINISHED)

        target_id = carpooling.car.user_id

        if author_id == target_id:
            raise bad_request(detail="You cannot review yourself")

        if author_id not in [p.user_id for p in carpooling.reservations]:
            raise forbidden(detail=self.USER_NOT_PARTICIPANT)

        opinion_data = {
            "comment": opinion.comment,
            "note": opinion.note,
            "status": OpinionStatusEnum.pending,
            "carpooling_id": carpooling.id,
            "author_id": author_id,
            "target_id": target_id,
        }
        try:
            opinion = await self.opinion_repository.create(opinion_data)
            await self.opinion_repository.db.commit()
            return opinion
        except IntegrityError:
            await self.opinion_repository.db.rollback()
            logger.exception("Integrity error while creating a new opinion")
            raise conflict(detail=self.OPINION_ALREADY_EXISTS)
        except Exception:
            await self.opinion_repository.db.rollback()
            logger.exception("Unexpected error while creating a new opinion")
            raise bad_request(detail="Error creating opinion")

    async def validate_opinion(self, opinion_id: int, opinion: OpinionStatusUpdate, validator_id: int) -> Opinion:
        """
        Validate or reject an opinion.

        Only users with the employee role can perform this action.
        The opinion must exist and be in a pending state.

        Args:
            opinion_id (int): The unique identifier of the opinion.
            opinion (OpinionStatusUpdate): The data containing the new status.
            validator_id (int): The unique identifier of the user validating the opinion.

        Raises:
            not_found:
                - If the user is not found.
                - If the user or opinion is not found.
                - If the opinion was not updated.
            forbidden:
                - If the user has not the 'employee' role.
            bad_request:
                - If the opinion is not in pending state.
                - If an error occurs while validating the opinion.
            conflict:
                - If the opinion already exists.

        Returns:
            Opinion: The updated opinion.
        """
        validator = await self.user_repository.get_user_with_roles(validator_id)

        if validator is None:
            raise not_found(detail=self.USER_NOT_FOUND)

        # Checks that the user has the 'employee' role
        roles = validator.roles
        is_employee = False
        for role in roles:
            if role.name == "employee":
                is_employee = True
                break

        if not is_employee:
            raise forbidden(detail=self.NOT_EMPLOYEE)

        # Checks current opinion exists
        current_opinion = await self.opinion_repository.get_by_id(opinion_id)
        if current_opinion is None:
            raise not_found(detail=self.OPINION_NOT_FOUND)

        # checks current opinion is pending status.
        if current_opinion.status != OpinionStatusEnum.pending:
            raise bad_request(detail=self.OPINION_NOT_PENDING)

        try:
            updated_opinion = await self.opinion_repository.update_status(opinion_id,
                                                                          opinion.status,
                                                                          validator.id,
                                                                          validated_at=datetime.now(timezone.utc))
            if updated_opinion is None:
                raise bad_request(detail=self.OPINION_NOT_UPDATED)
            await self.opinion_repository.db.commit()
            return updated_opinion
        except IntegrityError:
            await self.opinion_repository.db.rollback()
            logger.exception("Integrity error while updating a new opinion")
            raise conflict(detail=self.OPINION_ALREADY_EXISTS)
        except Exception:
            await self.opinion_repository.db.rollback()
            logger.exception("Unexpected error while updating a new opinion")
            raise bad_request(detail="Error updating opinion")

    async def get_rejected_opinions(self) -> list[Opinion]:
        """
        Retrieve all rejected opinions.

        Returns:
            list[Opinion]: List of rejected opinions.
        """
        return await self.opinion_repository.get_all_by_status_rejected()
