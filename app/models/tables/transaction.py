from decimal import Decimal
from datetime import datetime
from app.utils.transaction_type_enum import TransactionTypeEnum
from sqlalchemy import Integer, ForeignKey, Numeric, DateTime, func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship
from databases.postgresql import Base

class Transaction(Base):
    """
    Represents a transaction in the database.

    Attributes:
        id (int): The identifier of the transaction.
        amount (Decimal): The amount of the transaction.
        user_id (int): The user identifier of the transaction.
        carpooling_id (int): The carpooling identifier of the transaction.
        type (TransactionTypeEnum): The transaction type of the transaction.
        created_at (datetime): The date and time when the transaction was created.
    """
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(6,2), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    carpooling_id: Mapped[int] = mapped_column(Integer, ForeignKey('carpoolings.id'), nullable=False)
    transaction_type: Mapped[TransactionTypeEnum] = mapped_column(ENUM(TransactionTypeEnum,
                                                           name='transaction_type',
                                                           create_type=False),
                                                      nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())