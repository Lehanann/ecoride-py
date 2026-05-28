from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tables.transaction import Transaction
from decimal import Decimal
from utils.transaction_type_enum import TransactionTypeEnum


class TransactionRepository:
    """
    Repository handling database operations related to the transaction model.
    """
    def __init__(self, db: AsyncSession):
        """
        Initialize the TransactionRepository class.

        Args:
            db (AsyncSession): Asynchronous database session.
        """
        self.db = db

    async def get_by_user_id(self, user_id: int) -> list[Transaction]:
        """
        Retrieve all transactions for a given user.
        Args:
            user_id (int): The identifier of the user.

        Returns:
            list[Transaction]: List of user transactions.
        """
        return list(await self.db.scalars(select(Transaction)
                                          .where(Transaction.user_id == user_id)
                                          .order_by(Transaction.created_at.desc())
                                          )
                    )

    async def get_by_carpooling_id(self, carpooling_id: int) -> list[Transaction]:
        """
        Retrieve all transactions related to a carpooling.

        Args:
            carpooling_id (int): Identifier of the carpooling.

        Returns:
            list[Transaction]: List of transactions for the carpooling.
        """
        return list(await self.db.scalars(select(Transaction)
                                          .where(Transaction.carpooling_id == carpooling_id)
                                          .order_by(Transaction.created_at.desc())
                                          )
                    )

    async def create(self, user_id: int, amount: Decimal, carpooling_id: int, transaction_type: TransactionTypeEnum ) -> Transaction:
        """
        Create a new transaction.
        Args:
            user_id (int): The identifier of the user.
            amount (Decimal): The amount of the transaction.
            carpooling_id (int): The identifier of the carpooling.
            transaction_type (TransactionTypeEnum): The type of transaction.

        Returns:
            Transaction: The newly created transaction.
        """
        transaction = Transaction(
            user_id = user_id,
            amount = amount,
            carpooling_id = carpooling_id,
            transaction_type = transaction_type
        )
        self.db.add(transaction)
        return transaction

