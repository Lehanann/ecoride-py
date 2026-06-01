from fastapi import HTTPException, status
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.carpooling_repository import CarpoolingRepository
from app.repositories.user_repository import UserRepository
from app.utils.carpooling_status_enum import CarpoolingStatusEnum
from app.utils.transaction_type_enum import TransactionTypeEnum
from decimal import Decimal

class TransactionService:
    """
    Service handling business logic related to transactions.
    Includes creation and retrieval workflows.
    """
    def __init__(self,
                 transaction_repository: TransactionRepository,
                 carpooling_repository: CarpoolingRepository,
                 user_repository: UserRepository) -> None:
        """
        Initialize the reservation service.

        Args:
            transaction_repository (TransactionRepository): The repository of the reservation.
            carpooling_repository (CarpoolingRepository): The repository of the carpooling.
            user_repository (UserRepository): The repository of the user.
        """
        self.transaction_repository = transaction_repository
        self.carpooling_repository = carpooling_repository
        self.user_repository = user_repository

    async def generate_transactions(self, carpooling_id: int) -> None:
        """
        Generate the transactions for the given carpooling id.

        Args:
            carpooling_id (int): the unique identifier of the carpooling.
        """
        carpooling = await self.carpooling_repository.get_by_id(carpooling_id)
        if carpooling is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carpooling not found")

        if carpooling.status != CarpoolingStatusEnum.finished:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Carpooling not finished")

        ecoride = await self.user_repository.get_by_username("administrator")
        if ecoride is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin not found")

        driver = carpooling.car.user
        passengers = [r.user for r in carpooling.reservations]
        amount = Decimal(str(carpooling.price))
        COMMISSION = Decimal("2")
        driver_amount = amount - COMMISSION

        try:
            for passenger in passengers:


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
                    amount=COMMISSION,
                    carpooling_id=carpooling.id,
                    transaction_type=TransactionTypeEnum.commission
                )
                ecoride.credit += COMMISSION
            await self.transaction_repository.db.commit()
        except Exception:
            await self.transaction_repository.db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transaction error")