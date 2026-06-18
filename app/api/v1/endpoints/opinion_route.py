from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.opinion_repository import OpinionRepository
from app.repositories.user_repository import UserRepository
from app.repositories.carpooling_repository import CarpoolingRepository
from app.schemas.opinion_schema import OpinionCreate, OpinionRead, OpinionStatusUpdate
from app.services.opinion_service import OpinionService
from databases.postgresql import get_session

router = APIRouter(prefix="/opinions", tags=["opinions"])

def get_service_opinion(db: AsyncSession = Depends(get_session)) -> OpinionService:
    """
    Provide an instance of OpinionService with injected repositories.
    """
    return OpinionService(OpinionRepository(db), UserRepository(db), CarpoolingRepository(db))

def get_repository_user(db: AsyncSession = Depends(get_session)) -> UserRepository:
    """
    Provide an instance of UserRepository.
    """
    return UserRepository(db)


@router.get("/pending", response_model=list[OpinionRead])
async def get_pending_opinions(request: Request,
                               opinion_service: OpinionService = Depends(get_service_opinion),
                               user_repository: UserRepository = Depends(get_repository_user)
                               ) -> list[OpinionRead]:
    """
    Retrieve all opinions awaiting validation.

    Only accessible by users with employee or admin roles.

    Args:
        request (Request): Incoming request containing the authenticated user ID.
        opinion_service (OpinionService): The service layer for handling opinion-related operations.
            This is injected automatically using Depends(get_service_opinion).
        user_repository (UserRepository): Repository used to retrieve user information.
            This is injected automatically using Depends(get_repository_user).

    Returns:
        list[OpinionRead]: The list of pending opinions.

    Raises:
        HTTPException:
            - 404 if user is not found
            - 403 if user is not authorized
    """
    validator_id = request.state.user_id

    current_user = await user_repository.get_user_with_roles(validator_id)
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not any(role.name in ["employee","administrator"] for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return await opinion_service.get_pending_opinions()

@router.get("/me", response_model=list[OpinionRead])
async def get_driver_opinions(request: Request,
                              opinion_service: OpinionService = Depends(get_service_opinion)
                              ) -> list[OpinionRead]:
    """
    Retrieve all approved opinions received by the current user.

    Args:
        request (Request): Incoming request containing the authenticated user ID.
        opinion_service (OpinionService): The service layer for handling opinion-related operations.
            This is injected automatically using Depends(get_service_opinion).

    Returns:
        list[OpinionRead]: List of approved opinions.
    """
    driver_id = request.state.user_id

    return await opinion_service.get_opinions_for_driver(driver_id)

@router.post("/",response_model=OpinionRead, status_code=status.HTTP_201_CREATED)
async def create_opinion(request: Request,
                         data: OpinionCreate,
                         opinion_service: OpinionService = Depends(get_service_opinion)
                         ) -> OpinionRead:
    """
    Create a new opinion for a completed carpooling.

    Args:
        request (Request): Incoming request containing the authenticated user ID.
        data (OpinionCreate): The data used to create the opinion.
        opinion_service (OpinionService): The service layer for handling opinion-related operations.
            This is injected automatically using Depends(get_service_opinion).

    Returns:
        OpinionRead: The created opinion.
    """
    author_id = request.state.user_id
    opinion_created = await opinion_service.create_opinion(author_id, data)
    return opinion_created

@router.patch("/{opinion_id}", response_model=OpinionRead)
async def validate_opinion(request: Request,
                         opinion_id: int,
                         data: OpinionStatusUpdate,
                         opinion_service: OpinionService = Depends(get_service_opinion)
                         ) -> OpinionRead:
    """
    Validate or reject an opinion.

    Args:
        request (Request): Incoming request containing the authenticated user ID.
        opinion_id (int): Identifier of the opinion.
        data (OpinionStatusUpdate): New status data for the opinion.
        opinion_service (OpinionService): The service layer for handling user-related operations.
            This is injected automatically using Depends(get_service_opinion).

    Returns:
        OpinionRead: The updated opinion.
    """
    validator_id = request.state.user_id
    updated = await opinion_service.validate_opinion(opinion_id, data, validator_id)
    return updated
