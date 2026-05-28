from fastapi import HTTPException
from psycopg import IntegrityError
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.carpooling_repository import CarpoolingRepository
from app.repositories.user_repository import UserRepository
from utils.carpooling_status_enum import CarpoolingStatusEnum
from utils.transaction_type_enum import TransactionTypeEnum
from decimal import Decimal


class TransactionService:
    """
    Service handling business logic related to transactions.
    Includes creation and retrieval workflows.
    """
    def __init__(self, transaction_repository: TransactionRepository, carpooling_repository: CarpoolingRepository, user_repository: UserRepository) -> None:
        self.transaction_repository = transaction_repository
        self.carpooling_repository = carpooling_repository
        self.user_repository = user_repository

    async def generate_transactions(self, carpooling_id: int):

        carpooling = await self.carpooling_repository.get_by_id(carpooling_id)
        if carpooling is None:
            raise HTTPException(status_code=404, detail="Carpooling not found")

        if carpooling.status != CarpoolingStatusEnum.finished:
            raise HTTPException(status_code=400, detail="Carpooling not finished")

        ecoride = await self.user_repository.get_by_username("administrator")
        if ecoride is None:
            raise HTTPException(status_code=404, detail="Admin not found")

        driver = carpooling.car.user
        passengers = [r.user for r in carpooling.reservations]

        try:
            for passenger in passengers:
                amount = Decimal(str(carpooling.price))
                commission = Decimal("2")
                driver_amount = amount - commission

                # debit passenger
                await self.transaction_repository.create(
                    user_id=passenger.id,
                    amount=-amount,
                    carpooling_id=carpooling.id,
                    transaction_type=TransactionTypeEnum.payment
                )
                passenger.credit -= amount

                # credit driver
                await self.transaction_repository.create(
                    user_id=driver.id,
                    amount=driver_amount,
                    carpooling_id=carpooling.id,
                    transaction_type=TransactionTypeEnum.payment
                )
                driver.credit += driver_amount

                # commission
                await self.transaction_repository.create(
                    user_id=ecoride.id,
                    amount=commission,
                    carpooling_id=carpooling.id,
                    transaction_type=TransactionTypeEnum.commission
                )
                ecoride.credit += commission

        except IntegrityError:
            raise HTTPException(status_code=400, detail="Transaction error")