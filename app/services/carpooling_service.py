import logging
from sqlalchemy.exc import IntegrityError
from app.core.exceptions.http_exceptions import bad_request, forbidden, not_found, conflict
from datetime import date
from app.models.tables.carpooling import Carpooling
from app.repositories.carpooling_repository import CarpoolingRepository
from app.repositories.user_repository import UserRepository
from app.schemas.carpooling_schema import CarpoolingCreate, CarpoolingUpdate,CarpoolingStatusUpdate
from app.utils.carpooling_status_enum import CarpoolingStatusEnum
from app.services.transaction_service import TransactionService

logger = logging.getLogger(__name__)

class CarpoolingService:
    """
     Carpooling service that performs operations on the carpooling repository such as reading, creating, updating carpoolings.
    """

    CARPOOLING_NOT_FOUND = "Carpooling not found"
    CARPOOLING_ALREADY_EXISTS = "Carpooling already exists"
    USER_NOT_FOUND = "User not found"
    STATUS_NOT_FOUND = "Status not found"
    NOT_DRIVER = "The user has not the 'driver' role"
    CAR_NOT_OWNED = "The car does not belong to the user"
    INVALID_STATUS_TRANSITION = "Invalid status transition"

    def __init__(self,
                 carpooling_repository: CarpoolingRepository,
                 user_repository: UserRepository,
                 transaction_service: TransactionService
                 ) -> None:
        """
        Initialize the carpooling service.

        Args:
            carpooling_repository (CarpoolingRepository): The repository of the carpooling.
            user_repository (UserRepository): The repository of the user.
            transaction_service (TransactionService): The service of the transaction.
        """
        self.carpooling_repository = carpooling_repository
        self.user_repository = user_repository
        self.transaction_service = transaction_service

    async def get_carpooling_by_id(self, carpooling_id: int) -> Carpooling:
        """
        Retrieve a carpooling by its ID.

        Args:
            carpooling_id (int): The ID of the carpooling.

        Raises:
            not_found:
                - if the carpooling is not found.

        Returns:
            Carpooling: A carpooling matching the given ID.
        """
        carpooling = await self.carpooling_repository.get_by_id(carpooling_id)
        if carpooling is None:
            raise not_found(detail=self.CARPOOLING_NOT_FOUND)
        return carpooling

    async def get_public_carpooling_by_id(self, carpooling_id: int) -> Carpooling:
        """
        Retrieve a publicly visible carpooling by its ID.

        This method applies business rules before returning the carpooling:
        - The carpooling must have a status of `published`.
        - The carpooling must be scheduled for a date strictly later than today.

        Carpoolings that do not meet these criteria are treated as not found.

        Args:
            carpooling_id (int): The ID of the carpooling to retrieve.

        Raises:
            not_found:
                - If the carpooling is not found or is not publicly visible.

        Returns:
            Carpooling: The carpooling matching the given ID.
        """
        carpooling = await self.get_carpooling_by_id(carpooling_id)

        if carpooling.status != CarpoolingStatusEnum.published or carpooling.departure_date <= date.today():
            raise not_found(detail=self.CARPOOLING_NOT_FOUND)
        return carpooling

    async def get_all_carpoolings(self) -> list[Carpooling]:
        """
        Retrieve all publicly available carpoolings.

        This method applies business rules before returning carpooling:
        - Only carpoolings with status 'published' are included.
        - Only carpoolings with a departure date strictly greater than today are included.

        Carpoolings that are not published or whose departure date has already passed
        are intentionally excluded from the result.

        Returns:
            list(Carpooling): A list of available carpoolings matching the business rules.
        """
        carpooling_filtered = []
        carpoolings = await self.carpooling_repository.get_all()

        for carpooling in carpoolings:
            if carpooling.status == CarpoolingStatusEnum.published and carpooling.departure_date > date.today():
                carpooling_filtered.append(carpooling)

        return carpooling_filtered

    async def create_carpooling(self, carpooling: CarpoolingCreate, user_id: int) -> Carpooling:
        """
        Create a new carpooling.

        This method applies business rules before creating a new carpooling:
        - Ensures the user exists.
        - Ensures the user has the 'driver' role.
        - Ensures the selected car belongs to the user.
        - Ensures business constraints such as dates and price are valid.

        The newly created carpooling is created with a default status of `draft`.
        Status transitions are handled by a dedicated workflow.

        Args:
            carpooling (CarpoolingCreate): Schema containing the fields required to create a carpooling.
            user_id (int): The ID of the authenticated user creating the carpooling.

        Raises:
            not_found:
                - If business rules are violated or required resources are not found.
            forbidden:
                - if the user has not the 'driver' role.
            bad_request:
                - if departure date is in the past.
                - if departure date is greater than the end date.
                - if departure time is greater than the end date.
                - if the price is less than or equal to 2.
                - if the car does not belong to the user.
                - if creating car fails.
            conflict:
                - if the carpooling already exists.

        Returns:
            Carpooling: The newly created carpooling instance.
        """
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise not_found(detail=self.USER_NOT_FOUND)

        roles = user.roles
        is_driver = False
        for role in roles:
            if role.name == 'driver':
                is_driver = True
                break
        if not is_driver:
            raise forbidden(detail=self.NOT_DRIVER)

        if carpooling.departure_date < date.today():
            raise bad_request(detail="The departure date cannot be in the past")
        if carpooling.departure_date > carpooling.end_date:
            raise bad_request(detail="The departure date cannot be greater than the end date")
        if carpooling.departure_time > carpooling.end_time:
            raise bad_request(detail="The departure time cannot be greater than the end time")
        if carpooling.price <= 2:
            raise bad_request(detail="The price cannot be less than 2")

        user_car_ids = []
        for car in user.cars:
            user_car_ids.append(car.id)

        if carpooling.car_id not in user_car_ids:
            raise forbidden(detail=self.CAR_NOT_OWNED)

        carpooling_data = {
            "departure_date": carpooling.departure_date,
            "departure_time": carpooling.departure_time,
            "departure_location": carpooling.departure_location,
            "end_date": carpooling.end_date,
            "end_time": carpooling.end_time,
            "end_location": carpooling.end_location,
            "place_number": carpooling.place_number,
            "price": carpooling.price,
            "car_id": carpooling.car_id
        }

        try:
            new_carpooling = await self.carpooling_repository.create(carpooling_data)
            await self.carpooling_repository.db.commit()
            return new_carpooling
        except IntegrityError:
            await self.carpooling_repository.db.rollback()
            logger.exception("Integrity error while creating a new carpooling")
            raise conflict(detail=self.CARPOOLING_ALREADY_EXISTS)
        except Exception:
            await self.carpooling_repository.db.rollback()
            logger.exception("Unexpected error while creating a new carpooling")
            raise bad_request(detail="Error creating carpooling")

    async def update_carpooling(self, carpooling_id: int, data: CarpoolingUpdate, user_id: int) -> Carpooling:
        """
        Update an existing carpooling.

        This method applies business rules before updating a carpooling:
        - Ensures the user exists.
        - Ensures the carpooling exists.
        - Ensures the user has the 'driver' role.
        - Ensures the carpooling (or the updated car) belongs to the user.

        Only structural fields of the carpooling can be updated here.
        The carpooling status is handled through a dedicated workflow
        and is intentionally not modified by this method.

        Args:
            carpooling_id (int): The ID of the carpooling to update.
            data (CarpoolingUpdate): Schema containing the fields to update.
            user_id (int): The ID of the authenticated user performing the update.

        Raises:
            not_found:
                - If the user is not found.
                - if The carpooling is not found.
            forbidden:
                - if the user is not allowed to modify the carpooling.
                - if the user has not the 'driver' role.
                - if the car does not belong to the user.
            conflict:
                - if the carpooling already exists.
            bad_request:
                -  if an error occurs while updating the carpooling.

        Returns:
            Carpooling: The updated carpooling instance.
        """
        user = await self.user_repository.get_by_id(user_id)
        carpooling = await self.carpooling_repository.get_by_id(carpooling_id)

        # check that user exists
        if user is None:
            raise not_found(detail=self.USER_NOT_FOUND)

        # Collect all car IDs owned by the user
        user_car_ids = []
        for car in user.cars:
            user_car_ids.append(car.id)

        # check that carpooling exists
        if carpooling is None:
            raise not_found(detail=self.CARPOOLING_NOT_FOUND)

        # Checks that the user has the 'driver' role
        roles = user.roles
        is_driver = False
        for role in roles:
            if role.name == 'driver':
                is_driver = True
                break

        if not is_driver:
            raise forbidden(detail=self.NOT_DRIVER)

        # Extract only fields provided in the update payload
        carpooling_data = data.model_dump(exclude_unset=True)

        # Determine the final car ID (updated or original)
        final_car_id = carpooling_data.get("car_id", carpooling.car_id)

        # Ensure the car used by the carpooling belongs to the user
        if final_car_id not in user_car_ids:
            raise forbidden(detail=self.CAR_NOT_OWNED)

        try:
            updated_carpooling = await self.carpooling_repository.update(carpooling_id, carpooling_data)
            if updated_carpooling is None:
                raise not_found(detail=self.CARPOOLING_NOT_FOUND)
            await self.carpooling_repository.db.commit()
            return updated_carpooling
        except IntegrityError:
            await self.carpooling_repository.db.rollback()
            logger.exception("Integrity error while updating the carpooling")
            raise conflict(detail=self.CARPOOLING_ALREADY_EXISTS)
        except Exception:
            await self.carpooling_repository.db.rollback()
            logger.exception("Unexpected error while updating carpooling")
            raise bad_request(detail="Error updating carpooling")

    async def update_status_carpooling(self, carpooling_id: int, data: CarpoolingStatusUpdate, user_id: int) -> Carpooling:
        """
        Update the status of the carpooling only.

        This method applies business rules before updating the status of carpooling:
        - Ensures the user exists.
        - Ensures the carpooling exists.
        - Ensures the user has the 'driver' role.
        - Ensures the carpooling (or the updated car) belongs to the user.

        Only status field of the carpooling can be updated here.
        This workflow dedicated to the status of the carpooling.

        Args:
            carpooling_id (int): The ID of the carpooling to update.
            data (CarpoolingStatusUpdate): Schema containing the field status to update.
            user_id (int): The ID of the authenticated user performing the update.

        Raises:
            not_found:
                - If the user is not found.
                - if The carpooling is not found.
                - if the status of the carpooling is not found.
            forbidden:
                - if the user is not allowed to modify the carpooling.
                - if the user has not the 'driver' role.
                - if the car does not belong to the user.
            conflict:
                - if the status of the carpooling already exists.
            bad_request:
                -  if an error occurs while updating the status of the carpooling.

        Returns:
            Carpooling: The updated carpooling instance.
        """
        user = await self.user_repository.get_by_id(user_id)
        carpooling = await self.carpooling_repository.get_by_id(carpooling_id)

        # check that user exists
        if user is None:
            raise not_found(detail=self.USER_NOT_FOUND)

        # check that carpooling exists
        if carpooling is None:
            raise not_found(detail=self.CARPOOLING_NOT_FOUND)

        # Checks that the user has the 'driver' role
        roles = user.roles
        is_driver = False
        for role in roles:
            if role.name == 'driver':
                is_driver = True
                break

        if not is_driver:
            raise forbidden(detail=self.NOT_DRIVER)

        # Collect all car IDs owned by the user
        user_car_ids = []
        for car in user.cars:
            user_car_ids.append(car.id)

        if carpooling.car_id not in user_car_ids:
            raise forbidden(detail=self.CAR_NOT_OWNED)

        new_status: CarpoolingStatusEnum
        # Workflow allowed scenario to change the status of the carpooling.
        if carpooling.status == CarpoolingStatusEnum.draft:
            if data.status == CarpoolingStatusEnum.published:
                new_status = CarpoolingStatusEnum.published
            elif data.status == CarpoolingStatusEnum.cancelled:
                new_status = CarpoolingStatusEnum.cancelled
            else:
                raise bad_request(detail=self.INVALID_STATUS_TRANSITION)
        elif carpooling.status == CarpoolingStatusEnum.published:
            if data.status == CarpoolingStatusEnum.finished:
                new_status = CarpoolingStatusEnum.finished
            elif data.status == CarpoolingStatusEnum.cancelled:
                new_status = CarpoolingStatusEnum.cancelled
            else:
                raise bad_request(detail=self.INVALID_STATUS_TRANSITION)

        else:
            raise bad_request(detail=self.INVALID_STATUS_TRANSITION)

        try:
            old_status = carpooling.status
            updated_carpooling = await self.carpooling_repository.update_status(carpooling_id, new_status)
            if updated_carpooling is None:
                raise not_found(detail=self.CARPOOLING_NOT_FOUND)
            if old_status != CarpoolingStatusEnum.finished and new_status == CarpoolingStatusEnum.finished:
                await self.transaction_service.generate_transactions(carpooling.id)

            await self.carpooling_repository.db.commit()
            return updated_carpooling
        except IntegrityError:
            await self.carpooling_repository.db.rollback()
            logger.exception("Integrity error while updating the carpooling")
            raise conflict(detail=self.CARPOOLING_ALREADY_EXISTS)
        except Exception:
            await self.carpooling_repository.db.rollback()
            logger.exception("Error while updating the status of the carpooling")
            raise bad_request(detail="Error updating carpooling")