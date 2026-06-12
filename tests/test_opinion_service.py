import pytest
from app.services.opinion_service import OpinionService
from app.utils.carpooling_status_enum import CarpoolingStatusEnum
from app.utils.opinion_status_enum import OpinionStatusEnum
from fastapi import HTTPException

class FakeUserRepository:
    def __init__(self, user):
        self.user = user

    async def get_by_id(self, user_id):
        if self.user.id == user_id:
            return self.user
        return None

class FakeCarpoolingRepository:
    def __init__(self, carpooling):
        self.carpooling = carpooling

    async def get_by_id(self, carpooling_id):
        return self.carpooling

class FakeOpinionRepository:
    def __init__(self):
        self.created = None
        self.opinion = None

    async def create(self, opinion_data):
        self.created = opinion_data
        return type("Opinion",(),opinion_data)()

    async def get_by_id(self, opinion_id):
        return self.opinion

    async def update_status(self, opinion_id, status, validator_id, **kwargs):
        self.opinion.status = status
        self.opinion.validator_id = validator_id
        return self.opinion


    @property
    def db(self):
        return self

    async def commit(self):
        pass

    async def rollback(self):
        pass


class FakeUser:
    def __init__(self, id, role):
        self.id = id
        self.roles = [type("Role", (), {"name": role})()]

class FakeCarpooling:
    def __init__(self, driver_id, passengers_ids):
        self.id = 1
        self.status = CarpoolingStatusEnum.finished

        self.car = type("Car", (), {"user_id": driver_id})()

        self.reservations = [
            type("Reservation", (), {"user_id": pid})()
            for pid in passengers_ids
        ]


class FakeReservation:
    def __init__(self, user_id):
        self.user_id = user_id

class FakeCar:
    def __init__(self, user_id):
        self.user_id = user_id

class FakeOpinion:
    def __init__(self):
        self.id = 1
        self.status = OpinionStatusEnum.pending



@pytest.mark.asyncio
async def test_create_opinion_success():

    # Arrange
    author = FakeUser(id=2,role="passenger")

    carpooling = FakeCarpooling(
        driver_id=1,
        passengers_ids=[2]
    )

    user_repo = FakeUserRepository(author)
    carpooling_repo = FakeCarpoolingRepository(carpooling)
    opinion_repo = FakeOpinionRepository()

    service = OpinionService(
        opinion_repo,
        user_repo,
        carpooling_repo
    )

    fake_schema = type(
        "Schema",
        (),
        {
            "comment": "good",
            "note": 5,
            "carpooling_id": 1
        }
    )()

    # Act
    result = await service.create_opinion(2, fake_schema)

    # Assert
    assert result.comment == "good"
    assert result.author_id == 2

@pytest.mark.asyncio
async def test_validate_opinion_success():
    # Arrange
    validator = FakeUser(id=5, role="employee")

    carpooling = FakeCarpooling(
        driver_id=1,
        passengers_ids=[2]
    )

    opinion = FakeOpinion()

    user_repo = FakeUserRepository(validator)
    carpooling_repo = FakeCarpoolingRepository(carpooling)
    opinion_repo = FakeOpinionRepository()
    opinion_repo.opinion = opinion

    service = OpinionService(
        opinion_repo,
        user_repo,
        carpooling_repo
    )

    fake_schema = type(
        "Schema",
        (),
        {
            "status": OpinionStatusEnum.approved
        }
    )()

    # Act
    result = await service.validate_opinion(
        opinion_id=1,
        opinion=fake_schema,
        validator_id=5
    )

    # Assert
    assert result.status == OpinionStatusEnum.approved

@pytest.mark.asyncio
async def test_validate_opinion_forbidden_if_not_employee():
    validator = FakeUser(id=5, role="passenger")
    carpooling = FakeCarpooling(
        driver_id=1,
        passengers_ids=[2]
    )
    opinion = FakeOpinion()

    user_repo = FakeUserRepository(validator)
    carpooling_repo = FakeCarpoolingRepository(carpooling)
    opinion_repo = FakeOpinionRepository()
    opinion_repo.opinion = opinion

    service = OpinionService(
        opinion_repo,
        user_repo,
        carpooling_repo
    )
    fake_schema = type(
        "Schema",
        (),
        {
            "status": OpinionStatusEnum.approved
        }
    )()

    with pytest.raises(HTTPException) as exc:
        await service.validate_opinion(
            opinion_id=1,
            opinion=fake_schema,
            validator_id=5
        )

    assert exc.value.status_code == 403

@pytest.mark.asyncio
async def test_validate_opinion_fails_if_not_pending():
    validator = FakeUser(id=5, role="employee")
    carpooling = FakeCarpooling(
        driver_id=1,
        passengers_ids=[2]
    )
    opinion = FakeOpinion()
    opinion.status = OpinionStatusEnum.approved
    user_repo = FakeUserRepository(validator)
    carpooling_repo = FakeCarpoolingRepository(carpooling)
    opinion_repo = FakeOpinionRepository()
    opinion_repo.opinion = opinion

    service = OpinionService(
        opinion_repo,
        user_repo,
        carpooling_repo
    )
    fake_schema = type(
        "Schema",
        (),
        {
            "status": OpinionStatusEnum.approved
        }
    )()

    with pytest.raises(HTTPException) as exc:
        await service.validate_opinion(
            opinion_id=1,
            opinion=fake_schema,
            validator_id=5
        )

    assert exc.value.status_code == 400