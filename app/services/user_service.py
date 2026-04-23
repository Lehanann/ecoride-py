from fastapi import UploadFile
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import UserCreate
from app.services.file_service import FileService

class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def create_user(self, data: UserCreate, avatar: UploadFile | None):

        if avatar:
            avatar_url: str = FileService.save_profile_image(avatar)
            data.avatar_url = avatar_url

        return await self.repository.create(data)


