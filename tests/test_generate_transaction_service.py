from app.utils.carpooling_status_enum import CarpoolingStatusEnum
import pytest
from decimal import Decimal
from app.services.transaction_service import TransactionService
from fastapi import HTTPException



class FakeTransactionRepository:
    def __init__(self):
        self.transactions = []

    async def create(self, **kwargs):
        self.transactions.append(kwargs)

    async def get_by_carpooling_id(self, carpooling_id):
        return [t for t in self.transactions if t["carpooling_id"] == carpooling_id]

    @property
    def db(self):
        return self

    async def commit(self):
        pass

    async def rollback(self):
        pass

class FakeUserRepository:
    def __init__(self, platform_user):
        self.platform_user = platform_user

    async def get_by_username(self, username):
        return self.platform_user



class FakeCarpoolingRepository:
    def __init__(self, carpooling):
        self.carpooling = carpooling

    async def get_by_id(self, carpooling_id):
        return self.carpooling

class FakeUser:
    def __init__(self, user_id, credit=0):
        self.id = user_id
        self.credit = credit


class FakeReservation:
    def __init__(self, user):
        self.user = user


class FakeCar:
    def __init__(self, user):
        self.user = user


class FakeCarpooling:
    def __init__(self, car, reservations, price):
        self.id = 1
        self.car = car
        self.reservations = reservations
        self.price = price
        self.status = CarpoolingStatusEnum.finished


@pytest.mark.asyncio
async def test_generate_transactions_success():
    # Arrange

    # driver
    driver = FakeUser(user_id=1, credit=0)

    # passengers
    passenger1 = FakeUser(user_id=2, credit=100)
    passenger2 = FakeUser(user_id=3, credit=100)

    reservations = [
        FakeReservation(passenger1),
        FakeReservation(passenger2),
    ]

    car = FakeCar(driver)

    carpooling = FakeCarpooling(
        car=car,
        reservations=reservations,
        price=10
    )

    # platform user (administrator)
    platform_user = FakeUser(user_id=99, credit=0)

    transaction_repo = FakeTransactionRepository()
    carpooling_repo = FakeCarpoolingRepository(carpooling)
    user_repo = FakeUserRepository(platform_user)

    service = TransactionService(
        transaction_repo,
        carpooling_repo,
        user_repo
    )

    # Act
    await service.generate_transactions(carpooling.id)

    # Assert
    # 👉 nombre de transactions
    assert len(transaction_repo.transactions) == 6  # 2 passengers x 3 transactions

    # 👉 crédits mis à jour
    assert passenger1.credit == 90
    assert passenger2.credit == 90

    assert driver.credit == 16  # 2 * (10 - 2)
    assert platform_user.credit == 4  # 2 * commission


@pytest.mark.asyncio
async def test_generate_transactions_already_exists():
    # Arrange
    driver = FakeUser(user_id=1)
    passenger = FakeUser(user_id=2)

    reservations = [FakeReservation(passenger)]
    car = FakeCar(driver)

    carpooling = FakeCarpooling(
        car=car,
        reservations=reservations,
        price=10
    )

    platform_user = FakeUser(user_id=99)

    transaction_repo = FakeTransactionRepository()

    # ✅ on simule une transaction existante
    transaction_repo.transactions.append({
        "carpooling_id": carpooling.id
    })

    carpooling_repo = FakeCarpoolingRepository(carpooling)
    user_repo = FakeUserRepository(platform_user)

    service = TransactionService(
        transaction_repo,
        carpooling_repo,
        user_repo
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc:
        await service.generate_transactions(carpooling.id)

    assert exc.value.status_code == 409