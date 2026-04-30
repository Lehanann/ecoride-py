from typing import List

from fastapi import HTTPException
from app.models.tables.brand import Brand
from app.repositories.brand_repository import BrandRepository
from app.schemas.brand_schema import BrandCreate, BrandUpdate


class BrandService:
    """
    Brand service that performs operations on the brand repository such as reading, creating, updating, and deleting brands.
    """
    def __init__(self, repository: BrandRepository) -> None:
        """
        Initialize the brand service with the brand repository.
        Args:
            repository:
        """
        self.repository = repository

    async def get_by_id(self, brand_id: int) -> Brand:
        """
        Get a brand from the repository by its id.
        Args:
            brand_id(int): The ID of the brand.
        Raises:
            HTTPException: if the ID of brand is not found.
        Returns:
             brand(Brand): The brand with the given ID.
        """
        brand = await self.repository.get_by_id(brand_id)
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        return brand

    async def get_by_name(self, name: str) -> Brand:
        """
        Get a brand from the repository by its name.
        Args:
            name str: The name of the brand.
        Raises:
            HTTPException: if the name is not found.
        Returns:
            brand(Brand): The brand with the given name.
        """
        brand = await self.repository.get_by_name(name)
        if not brand:
            raise HTTPException(status_code=404, detail="Brand not found")
        return brand

    async def get_all(self) -> List[Brand]:
        """
        Get all brands from the repository.
        Returns:
            list(Brand): A list of brands.
        """
        return await self.repository.get_all()

    async def create(self, data: BrandCreate) -> Brand:
        """
        Create a new brand from the repository.
        Args:
            data (BrandCreate):  The schema containing fields to create new instance brand.

        Returns:
            brand(Brand): The newly created instance of brand.
        """
        dataform = {
            "name": data.name,
        }

        try:
            return await self.repository.create(dataform)
        except Exception:
            raise HTTPException(status_code=400, detail="Error creating Brand")

    async def update(self, brand_id: int, data: BrandUpdate) -> Brand:
        """
        Update an existing brand from the repository.
        Args:
            brand_id (int): The ID of the brand to update.
            data (BrandUpdate): The schema containing fields to update an existing brand.:
        Raises:
            - HTTPException: if the ID of brand is not found.
            - HTTPException: if the ID of brand is not updated.
        Returns:
            update_brand(Brand): The updated brand with the given ID.
        """
        dataform = data.model_dump(exclude_unset=True)

        try:
            update_brand = await self.repository.update(brand_id, dataform)
            if update_brand is None:
                raise HTTPException(status_code=404, detail="Brand not found")
            return update_brand
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=400, detail="Error updating brand")
