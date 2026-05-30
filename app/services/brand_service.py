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
            repository (BrandRepository): The repository of the brand.
        """
        self.repository = repository

    async def get_by_id(self, brand_id: int) -> Brand:
        """
        Retrieve a brand by its id.

        Args:
            brand_id (int): The ID of the brand.

        Raises:
            HTTPException:
                - if brand is not found.

        Returns:
             Brand: The brand with the given ID.
        """
        brand = await self.repository.get_by_id(brand_id)
        if brand is None:
            raise HTTPException(status_code=404, detail="Brand not found")
        return brand

    async def get_by_name(self, name: str) -> Brand:
        """
        Retrieve a brand by its name.

        Args:
            name (str): The name of the brand.

        Raises:
            HTTPException:
                - if the name is not found.

        Returns:
            Brand: The brand with the given name.
        """
        brand = await self.repository.get_by_name(name)
        if brand is None:
            raise HTTPException(status_code=404, detail="Brand not found")
        return brand

    async def get_all(self) -> list[Brand]:
        """
        Retrieve all brands.

        Returns:
            list[Brand]: The list of the brands.
        """
        return await self.repository.get_all()

    async def create(self, data: BrandCreate) -> Brand:
        """
        Create a new brand.

        Args:
            data (BrandCreate):  The data required to create a brand.

        Raises:
            HTTPException:
                - if the data is not valid.

        Returns:
            Brand: The newly created brand.
        """
        brand_data = {
            "name": data.name,
        }

        try:
            new_brand = await self.repository.create(brand_data)
            await self.repository.db.commit()
            return new_brand
        except Exception:
            await self.repository.db.rollback()
            raise HTTPException(status_code=400, detail="Error creating brand")

    async def update(self, brand_id: int, data: BrandUpdate) -> Brand:
        """
        Update an existing brand.

        Args:
            brand_id (int): The ID of the brand to update.
            data (BrandUpdate): The fields to update.

        Raises:
            - HTTPException: if the brand is not found.
            - HTTPException: if an error occurs while updating the brand

        Returns:
            Brand: The updated brand with the given ID.
        """
        brand_data = data.model_dump(exclude_unset=True)

        try:
            updated_brand = await self.repository.update(brand_id, brand_data)
            if updated_brand is None:
                raise HTTPException(status_code=404, detail="Brand not found")
            await self.repository.db.commit()
            return updated_brand
        except Exception:
            await self.repository.db.rollback()
            raise HTTPException(status_code=400, detail="Error updating brand")

    async def delete(self, brand_id: int) -> Brand:
        """
        Delete a brand.

        Args:
            brand_id (int): The unique identifier of the brand.

        Raises:
            - HTTPException: if brand is not found.
            - HTTPException: if an error occurs while deleting the brand.

        Returns:
            Brand: The deleted brand with the given ID.
        """
        deleted_brand = await self.repository.get_by_id(brand_id)
        if deleted_brand is None:
            raise HTTPException(status_code=404, detail="Brand not found")
        try:
            await self.repository.delete(brand_id)
            await self.repository.db.commit()
            return deleted_brand
        except Exception:
            await self.repository.db.rollback()
            raise HTTPException(status_code=400, detail="Error deleting brand")