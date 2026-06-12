import pytest
from fastapi import HTTPException

from app.services.carpooling_service import CarpoolingService
from datetime import date, time


class FakeCarpoolingRepository:
    def __init__(self):
        self.carpooling = None
    async def create(self, carpooling_data):
        self.carpooling = carpooling_data
        return self.carpooling

    @property
    def db(self):
        return self

    async def commit(self):
        pass

    async def rollback(self):
        pass


class FakeUserRepository:
    def __init__(self, user):
        self.user = user

    async def get_by_id(self, user_id):
        return self.user

class FakeTransactionService:
    pass

class FakeUser:
    def __init__(self, user_id, role):
        self.id = user_id
        self.roles = [type("Role", (), {"name": role})()]
        self.cars = [type("Car",(),{"id": 1})()]


@pytest.mark.asyncio
async def test_create_carpooling_success():

    user = FakeUser(user_id=2,role="driver")

    carpooling_repo = FakeCarpoolingRepository()
    user_repo = FakeUserRepository(user)
    transaction_svc = FakeTransactionService()

    service = CarpoolingService(
        carpooling_repo,
        user_repo,
        transaction_svc
    )
    fake_schema = type(
        "Schema",
        (),
        {
            "departure_date": date(2026,12,12),
            "departure_time": time(9,30),
            "departure_location": "Middle East",
            "end_date": date(2026,12,12),
            "end_time": time(10,30),
            "end_location": "Center East",
            "place_number": 2,
            "price": 10.00,
            "car_id": 1
        }
    )()
    result = await service.create_carpooling(
        carpooling=fake_schema,
        user_id=2
    )

    assert result is not None

@pytest.mark.asyncio
async def test_create_carpooling_forbidden_if_not_driver():
    user = FakeUser(user_id=3, role="passenger")

    carpooling_repo = FakeCarpoolingRepository()
    user_repo = FakeUserRepository(user)
    transaction_svc = FakeTransactionService()

    service = CarpoolingService(
        carpooling_repo,
        user_repo,
        transaction_svc
    )
    fake_schema = type(
        "Schema",
        (),
        {
            "departure_date": date(2026, 12, 12),
            "departure_time": time(9, 30),
            "departure_location": "Middle East",
            "end_date": date(2026, 12, 12),
            "end_time": time(10, 30),
            "end_location": "Center East",
            "place_number": 2,
            "price": 10.00,
            "car_id": 1
        }
    )()

    with pytest.raises(HTTPException ) as exc:
        await service.create_carpooling(carpooling=fake_schema, user_id=3)

    assert exc.value.status_code == 403