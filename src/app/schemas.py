from decimal import Decimal
from datetime import datetime

import pydantic
from pydantic import BaseModel

from app.types import TransactionType


class Base(BaseModel):
    model_config = pydantic.ConfigDict(from_attributes=True)


class User(Base):
    id: str
    name: str
    balance: Decimal


class UserCreate(Base):
    id: str
    name: str

# REMOVE ME
class TransactionBase(Base):
    amount: Decimal
    type: TransactionType
    uid: str
    created_at: datetime
    user_id: str


class TransactionAdd(TransactionBase):
    ...


class Transaction(TransactionBase):
    ...


class UserBalance(Base):
    balance: Decimal
# END REMOVE ME


class BalanceHistory(Base):
    id: int
    user_id: str
    balance: Decimal
    created_at: datetime
