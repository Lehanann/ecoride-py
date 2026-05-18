from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.tables.role import Role

class RoleRepository:

    def __init__(self, db: AsyncSession):

        self.db = db

    async def get_by_name(self, name: str) -> Role | None:
        role = await self.db.execute(select(Role).where(Role.name == name))
        return role.scalars().one_or_none()