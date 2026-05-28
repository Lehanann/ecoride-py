from enum import Enum

class TransactionTypeEnum(str, Enum):
    payment = 'payment'
    commission = 'commission'
    refund = 'refund'