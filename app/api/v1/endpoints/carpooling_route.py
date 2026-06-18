from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.schemas.carpooling_schema import CarpoolingCreate, CarpoolingRead, CarpoolingUpdate, CarpoolingStatusUpdate
from app.services.carpooling_service import CarpoolingService
from app.repositories.carpooling_repository import CarpoolingRepository
from databases.postgresql import get_session
from app.services.transaction_service import TransactionService
from app.repositories.transaction_repository import TransactionRepository

router = APIRouter(prefix="/carpoolings", tags=["carpoolings"])

def get_service_carpooling(db: AsyncSession = Depends(get_session)) -> CarpoolingService:
    return CarpoolingService(CarpoolingRepository(db),
                             UserRepository(db),
                             TransactionService(TransactionRepository(db),
                                                CarpoolingRepository(db),
                                                UserRepository(db)
                                                )
                             )


@router.get("/", response_model=list[CarpoolingRead])
async def get_all_carpoolings(service: CarpoolingService = Depends(get_service_carpooling)):
    """
    Retrieve a list of all carpoolings.

    This endpoint fetches all carpoolings available stored in the database and returns
    them in the format specified by the CarpoolingRead schema.

    Args:
        service (CarpoolingService): The service layer for handling user-related operations.
            This is injected automatically using Depends(get_service_carpooling).

    Returns:
        list[CarpoolingRead]: List of all carpoolings represented using the 'CarpoolingRead' schema which
        includes relevant carpooling details such as ID.
    """
    return await service.get_all_carpoolings()

@router.get("/{carpooling_id}", response_model=CarpoolingRead)
async def get_public_carpooling(carpooling_id: int, service: CarpoolingService = Depends(get_service_carpooling)):
    """
    Retrieve a public carpooling by its ID.

    This endpoint fetches a public carpooling by its ID stored in the database and returns
    it in the format specified by the 'CarpoolingRead' schema.

    Args:
        carpooling_id (int): The unique identifier of the carpooling.
        service (CarpoolingService): The service layer for handling user-related operations.
            This is injected automatically using Depends(get_service_carpooling).

    Returns:
        CarpoolingRead: A carpooling represented using the 'CarpoolingRead'
        schema, which includes relevant carpooling details such as ID.
    """
    return await service.get_public_carpooling_by_id(carpooling_id)

@router.post("/", response_model=CarpoolingRead, status_code=status.HTTP_201_CREATED)
async def create_carpooling(request: Request,
                            data: CarpoolingCreate,
                            service: CarpoolingService = Depends(get_service_carpooling)):
    """
    Creates a new carpooling.

    Args:
        request (Request): Request containing the user identifier allowed by the middleware auth.
            we can retrieve the identifier of the user.
        data (CarpoolingCreate): Schema containing all data required to create the carpooling
        service (CarpoolingService): The service layer for handling user-related operations.
            This is injected automatically using Depends(get_service_carpooling).

    Returns:
        CarpoolingRead: A carpooling represented using the 'CarpoolingRead'
            schema, which includes relevant carpooling details such as ID.
    """

    user_id = request.state.user_id
    return await service.create_carpooling(data, user_id)

@router.patch("/{carpooling_id}", response_model=CarpoolingRead, status_code=status.HTTP_200_OK)
async def update_carpooling(request: Request,
                            carpooling_id: int,
                            data: CarpoolingUpdate,
                            service: CarpoolingService = Depends(get_service_carpooling)):
    """
    Updates a carpooling by its ID.

    Args:
        request (Request): Request containing the user identifier allowed by the middleware auth.
        carpooling_id (int): The unique identifier of the carpooling.
        data (CarpoolingUpdate): The data used to update the carpooling.
        service (CarpoolingService): The service layer for handling user-related operations.
            This is injected automatically using Depends(get_service_carpooling).

    Returns:
        CarpoolingRead: A carpooling represented using the 'CarpoolingRead'
        schema, which includes relevant carpooling details such as ID.
    """
    user_id = request.state.user_id
    return await service.update_carpooling(carpooling_id, data, user_id)

@router.patch("/{carpooling_id}/status", response_model=CarpoolingRead, status_code=status.HTTP_200_OK)
async def update_carpooling_status(request: Request,
                                   carpooling_id: int,
                                   data: CarpoolingStatusUpdate,
                                   service: CarpoolingService = Depends(get_service_carpooling)):
    """
    Updates a carpooling status by its ID.

    Args:
        request (Request): Request containing the user identifier allowed by the middleware auth.
        carpooling_id (int): The unique identifier of the carpooling.
        data (CarpoolingStatusUpdate): The status to update the carpooling.
        service (CarpoolingService): The service layer for handling user-related operations.
            This is injected automatically using Depends(get_service_carpooling).

    Returns:
        CarpoolingRead: A carpooling represents by the 'CarpoolingRead'
        schema, which includes relevant carpooling details such as ID.
    """
    user_id = request.state.user_id
    return await service.update_status_carpooling(carpooling_id, data, user_id)