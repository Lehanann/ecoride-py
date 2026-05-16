from datetime import date
from fastapi import HTTPException, status
from app.models.tables.carpooling import Carpooling
from app.repositories.carpooling_repository import CarpoolingRepository
from app.repositories.user_repository import UserRepository
from app.schemas.carpooling_schema import CarpoolingCreate, CarpoolingUpdate,CarpoolingStatusUpdate
from app.utils.carpooling_status_enum import CarpoolingStatusEnum


class CarpoolingService:

    def __init__(self, carpooling_repository: CarpoolingRepository, user_repository: UserRepository) -> None:
        """
        Initialize the carpooling service.

        Args:
            carpooling_repository:
            user_repository:
        """
        self.carpooling_repository = carpooling_repository
        self.user_repository = user_repository

    async def get_carpooling_by_id(self, carpooling_id: int) -> Carpooling:
        """
        Retrieve a carpooling by its ID.

        Args:
            carpooling_id (int): The ID of the carpooling to retrieve.

        Returns:
            Carpooling: A carpooling matching the given ID.

        Raises:
            HTTPException: if carpooling is not found.
        """
        carpooling = await self.carpooling_repository.get_by_id(carpooling_id)
        if not carpooling:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,)
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

        Returns:
            Carpooling: The carpooling matching the given ID.

        Raises:
            HTTPException: If the carpooling is not found or is not publicly visible.

        """
        carpooling = await self.get_carpooling_by_id(carpooling_id)

        if carpooling.status != CarpoolingStatusEnum.published or carpooling.departure_date <= date.today():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
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

        Returns:
            Carpooling: The newly created carpooling instance.

        Raises:
            HTTPException: If business rules are violated or required resources are not found.
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        roles = user.roles
        is_driver = False
        for role in roles:
            if role.name == 'driver':
                is_driver = True
                break
        if not is_driver:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        if carpooling.departure_date < date.today():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        if carpooling.departure_date > carpooling.end_date:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        if carpooling.departure_time > carpooling.end_time:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        if carpooling.price < 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        user_car_ids = []
        for car in user.cars:
            user_car_ids.append(car.id)

        if carpooling.car_id not in user_car_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        dataform = {
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
            return await self.carpooling_repository.create(dataform)
        except Exception:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)

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

        Returns:
            Carpooling: The updated carpooling instance.

        Raises:
            HTTPException: If the user or carpooling does not exist,
                if the user is not allowed to modify the carpooling,
                or if a conflict occurs during the update.
        """
        user = await self.user_repository.get_by_id(user_id)
        carpooling = await self.carpooling_repository.get_by_id(carpooling_id)

        # check that user exists
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        # Collect all car IDs owned by the user
        user_car_ids = []
        for car in user.cars:
            user_car_ids.append(car.id)

        # check that carpooling exists
        if not carpooling:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        # Checks that the user has the 'driver' role
        roles = user.roles
        is_driver = False
        for role in roles:
            if role.name == 'driver':
                is_driver = True
                break

        if not is_driver:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        # Extract only fields provided in the update payload
        dataform = data.model_dump(exclude_unset=True)

        # Determine the final car ID (updated or original)
        final_car_id = dataform.get("car_id", carpooling.car_id)

        # Ensure the car used by the carpooling belongs to the user
        if final_car_id not in user_car_ids:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        try:
            update_carpooling = await self.carpooling_repository.update(carpooling_id, dataform)
            if update_carpooling is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            return update_carpooling
        except Exception:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)

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

        Returns:
            Carpooling: The updated carpooling instance.

        Raises:
            HTTPException: If the user or carpooling does not exist,
                if the user is not allowed to modify the carpooling,
                or if a conflict occurs during the update.
        """
        user = await self.user_repository.get_by_id(user_id)
        carpooling = await self.carpooling_repository.get_by_id(carpooling_id)

        # check that user exists
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        # check that carpooling exists
        if not carpooling:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        # Checks that the user has the 'driver' role
        roles = user.roles
        is_driver = False
        for role in roles:
            if role.name == 'driver':
                is_driver = True
                break

        if not is_driver:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        # Collect all car IDs owned by the user
        user_car_ids = []
        for car in user.cars:
            user_car_ids.append(car.id)

        if carpooling.car_id not in user_car_ids:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

        new_status: CarpoolingStatusEnum
        # Workflow allowed scenario to change the status of the carpooling.
        if carpooling.status == CarpoolingStatusEnum.draft:
            if data.status == CarpoolingStatusEnum.published:
                new_status = CarpoolingStatusEnum.published
            elif data.status == CarpoolingStatusEnum.cancelled:
                new_status = CarpoolingStatusEnum.cancelled
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        elif carpooling.status == CarpoolingStatusEnum.published:
            if data.status == CarpoolingStatusEnum.finished:
                new_status = CarpoolingStatusEnum.finished
            elif data.status == CarpoolingStatusEnum.cancelled:
                new_status = CarpoolingStatusEnum.cancelled
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        try:
            update_carpooling = await self.carpooling_repository.update_status(carpooling_id, new_status)
            if update_carpooling is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            return update_carpooling
        except Exception:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT)
