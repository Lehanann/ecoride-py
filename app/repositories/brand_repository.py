from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tables.brand import Brand

class BrandRepository:
    """
    Brand repository providing CRUD operations for a given SQLAlchemy model.
    """
    def __init__(self, db: AsyncSession):
        """
        Initialize the Brand repository with database session.

        Args:
            db (AsyncSession): Asynchronous database session.
        """
        self.db = db

    async def get_by_id(self, brand_id: int) -> Brand | None:
        """
        Retrieve a brand instance by its ID

        Args:
            brand_id (int): The unique identifier of the brand.

        Returns:
            Brand | None: The brand instance if found, otherwise None.
        """
        return await self.db.get(Brand, brand_id)


    async def get_by_name(self, name: str) -> Brand | None:
        """
        Retrieve a brand instance by its name.

        Args:
            name (str): The name of the brand.

        Returns:
             Brand | None: The brand instance if found, otherwise None.
        """
        result = await self.db.scalars(select(Brand).where(Brand.name == name))
        return result.first()

    async def get_all(self) -> list[Brand]:
        """
        Retrieve all instances of brand from the database.

        Returns:
            list[Brand]: The list of all brand instances.
        """
        return list(await self.db.scalars(select(Brand)))

    async def create(self, data: dict ) -> Brand:
        """
        Create a new brand instance.

        Args:
            data (dict): Schema containing fields to create the brand instance.

        Returns:
             Brand: The new brand instance.
        """
        brand = Brand(**data)
        self.db.add(brand)
        return brand

    async def update(self, brand_id: int, data: dict) -> Brand | None:
        """
        Update an existing brand instance by its ID.

        Args:
            brand_id (int): The brand ID to update.
            data (dict): Schema containing fields to update the brand instance.

        Returns:
             Brand | None: The updated brand instance if found, otherwise None.
        """
        brand = await self.get_by_id(brand_id)
        if brand is None:
            return None

        for key, value in data.items():
            setattr(brand, key, value)
        return brand

    async def delete(self, brand_id: int) -> Brand | None:
        """
        Delete an existing brand instance by its ID.

        Args:
            brand_id (int): The brand ID to delete.

        Returns:
             Brand | None: The deleted brand instance if found, otherwise None.
        """
        deleted_brand = await self.get_by_id(brand_id)
        if deleted_brand is None:
            return None
        await self.db.delete(deleted_brand)
        return deleted_brand