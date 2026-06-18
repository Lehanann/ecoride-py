from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from databases.postgresql import get_session
from app.services.brand_service import BrandService
from app.repositories.brand_repository import BrandRepository
from app.schemas.brand_schema import BrandCreate, BrandUpdate, BrandRead

router = APIRouter(prefix="/brands", tags=["brands"])

def get_service_brand(db: AsyncSession = Depends(get_session)) -> BrandService:
    return BrandService(BrandRepository(db))

@router.get("/", response_model=list[BrandRead])
async def list_brands(service: BrandService = Depends(get_service_brand)):
    """
    Retrieves all brands.

    This endpoint fetches all brands stored in the database and returns
    them in the format specified by the BrandRead schema.

    Args:
        service (BrandService): The service layer for handling brand-related operations.
        This is injected automatically using Depends(get_service_brand).

    Returns:
        list[BrandRead]: List of all brands represented by the 'BrandRead' schema which
        includes relevant brand details such as name and ID.
    """
    return await service.get_all()

@router.get("/{brand_id}", response_model=BrandRead)
async def get_brand(brand_id: int, service: BrandService = Depends(get_service_brand)):
    """
    Retrieve a brand by its ID.

    This endpoint fetches a brand by its ID stored in the database and returns
    it in the format specified by the `BrandRead` schema.

    Args:
        brand_id (int): Unique identifier of the brand
        service (BrandService): The service layer for handling brand-related operations.
        This is injected automatically using `Depends(get_service_brand)`.

    Returns:
        BrandRead: A brand represented by the `BrandRead`
        schema, which includes relevant brand details such as name and ID.
    """
    return await service.get_by_id(brand_id)

@router.post("/", response_model=dict[str,str], status_code=status.HTTP_201_CREATED)
async def create(data: BrandCreate, service: BrandService = Depends(get_service_brand)):
    """
    Creates a new brand.

    Args:
        data (BrandCreate): The data required to create a brand.
        service (BrandService): The service layer for handling brand-related operations.
        This is injected automatically using `Depends(get_service_brand)`.

    Returns:
        dict[str,str]: A dictionary containing a success message if the brand was created successfully.
    """
    await service.create(data)
    return {"message": "Brand created successfully."}

@router.patch("/{brand_id}", response_model=dict[str,str], status_code=status.HTTP_200_OK)
async def update(brand_id: int, data: BrandUpdate, service: BrandService = Depends(get_service_brand)):
    """
    Update a brand by its ID.

    Args:
        brand_id (int): Unique identifier of the brand.
        data (BrandUpdate): The data used to update the brand.
        service (BrandService): The service layer for handling brand-related operations.
        This is injected automatically using `Depends(get_service_brand)`.

    Raises:
        HTTPException: if the name already exists or if the brand is not found by its ID.

    Returns:
        dict[str,str]: A dictionary containing a success message if the brand was updated successfully.
    """
    await service.update(brand_id, data)
    return {"message": "Brand updated successfully."}