from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tables.user import User
from app.schemas.user_schema import UserCreate, UserUpdate
from typing import Any, List
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        """

        :param user_id:
        :return:
        """
        return await self.db.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().one_or_none()

    async def get_all(self) -> List[User] | Any:
        result = await self.db.execute(select(User))
        return result.scalars().all()

    async def create(self, data: UserCreate) -> User:

        hashed_password = pwd_context.hash(data.password)

        user = User(
            email=data.email,
            username=data.username,
            firstname=data.firstname,
            lastname=data.lastname,
            phone=data.phone,
            address=data.address,
            password_hash=hashed_password,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update(self,user_id: int, data: UserUpdate) -> User:
        user = await self.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        updated_user = data.model_dump(exclude_unset=True)

        for key, value in updated_user.items():
            setattr(user, key, value)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user_id: int) ->  bool:
        user = await self.get_by_id(user_id)
        if not user:
            return False
        await self.db.delete(user)
        await self.db.commit()
        return True