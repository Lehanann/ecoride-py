import pytest
from app.services.user_service import UserService
from app.schemas.user_schema import UserCreate
from fastapi import HTTPException

class FakeUserRepository:
    def __init__(self):
        self.users = []

    async def create(self, user_data):
        user_data["id"] = len(self.users) + 1
        user = type("User", (), user_data)()
        user.roles = []
        self.users.append(user)
        return user

    async def get_by_id(self, user_id):
        return None

    @property
    def db(self):
        return self

    async def commit(self):
        pass

    async def rollback(self):
        pass


class FakeRoleRepository:
    async def get_by_name(self, name):
        return type("Role", (), {"name": name})()


# ✅ TEST
@pytest.mark.asyncio
async def test_create_user_success():
    # Arrange
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository()
    service = UserService(user_repo, role_repo)

    data = UserCreate(
        username="testuser",
        email="test@email.com",
        password="verystrongpassword1234",
        confirm_password="verystrongpassword1234",
    )

    # Act
    result = await service.create_user(data, avatar=None)

    # Assert
    assert result.username == "testuser"
    assert result.email == "test@email.com"
    assert len(result.roles) == 1



@pytest.mark.asyncio
async def test_create_user_password_mismatch():
    user_repo = FakeUserRepository()
    role_repo = FakeRoleRepository()
    service = UserService(user_repo, role_repo)

    data = UserCreate(
        username="testuser",
        email="test@email.com",
        password="verystrongpassword",
        confirm_password="differentpassword"
    )

    with pytest.raises(HTTPException) as exc:
        await service.create_user(data, avatar=None)

    assert "do not match" in str(exc.value.detail)

