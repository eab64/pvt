import datetime
import logging
import typing
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase

from app.types import TransactionType


logger = logging.getLogger(__name__)


METADATA: typing.Final = sa.MetaData()


class Base(DeclarativeBase):
    metadata = METADATA


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(sa.String(36), primary_key=True)
    # DELETE ME
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    balance: Mapped[Decimal]


class Transaction(Base):
    __tablename__ = "transactions"

    uid: Mapped[str] = mapped_column(sa.String(36), primary_key=True)
    type: Mapped[TransactionType]
    amount: Mapped[Decimal]
    created_at: Mapped[datetime.datetime]

    user_id: Mapped[str] = mapped_column(sa.String(36), sa.ForeignKey("users.id"))
    # END DELETE ME
