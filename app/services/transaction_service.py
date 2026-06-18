import logging
from sqlalchemy.exc import IntegrityError
from app.core.exceptions.http_exceptions import bad_request, not_found, conflict
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.carpooling_repository import CarpoolingRepository
from app.repositories.user_repository import UserRepository
from app.utils.carpooling_status_enum import CarpoolingStatusEnum
from app.utils.transaction_type_enum import TransactionTypeEnum
from decimal import Decimal

logger = logging.getLogger(__name__)

class TransactionService:
    """
    Service handling business logic related to transactions.
    Includes creation and retrieval workflows.
    """
    COMMISSION = Decimal("2")
    CARPOOLING_NOT_FOUND = "Carpooling not found"
    USER_NOT_FOUND = "User not found"
    CARPOOLING_NOT_FINISHED = "Carpooling not finished"
    TRANSACTION_ALREADY_EXISTS = "Transaction already exists"
    PLATFORM_USERNAME = "administrator"

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

        Raises:
            not_found:
                - If the carpooling id is not found.
                - if the platform user is not found.
            bad_request:
                - If the carpooling is not finished.
                - If an error occurs while generating transactions.
            conflict:
                - If the carpooling id already exists.

        Args:
            carpooling_id (int): the unique identifier of the carpooling.
        """
        carpooling = await self.carpooling_repository.get_by_id(carpooling_id)
        if carpooling is None:
            raise not_found(detail=self.CARPOOLING_NOT_FOUND)

        if carpooling.status != CarpoolingStatusEnum.finished:
            raise bad_request(detail=self.CARPOOLING_NOT_FINISHED)

        existing_transaction = await self.transaction_repository.get_by_carpooling_id(carpooling.id)
        if existing_transaction:
            raise conflict("Transactions already generated for this carpooling")

        platform_user = await self.user_repository.get_by_username(self.PLATFORM_USERNAME)
        if platform_user is None:
            raise not_found(detail=self.USER_NOT_FOUND)

        driver = carpooling.car.user
        passengers = [r.user for r in carpooling.reservations]
        amount = Decimal(str(carpooling.price))
        driver_amount = amount - self.COMMISSION

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
                    user_id=platform_user.id,
                    amount=self.COMMISSION,
                    carpooling_id=carpooling.id,
                    transaction_type=TransactionTypeEnum.commission
                )
                platform_user.credit += self.COMMISSION
            await self.transaction_repository.db.commit()
        except IntegrityError:
            await self.transaction_repository.db.rollback()
            logger.exception("Integrity error while generating transactions")
            raise conflict(detail=self.TRANSACTION_ALREADY_EXISTS)
        except Exception:
            await self.transaction_repository.db.rollback()
            logger.exception("Unexpected error while generating transactions")
            raise bad_request(detail="Error generating carpooling transactions")