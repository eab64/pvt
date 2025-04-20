import datetime
import logging
import typing
from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship

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

    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="user", lazy="selectin")
    balance_history: Mapped[list["BalanceHistory"]] = relationship("BalanceHistory", back_populates="user", lazy="selectin")


class Transaction(Base):
    __tablename__ = "transactions"

    uid: Mapped[str] = mapped_column(sa.String(36), primary_key=True)
    type: Mapped[TransactionType]
    amount: Mapped[Decimal]
    created_at: Mapped[datetime.datetime]

    user_id: Mapped[str] = mapped_column(sa.String(36), sa.ForeignKey("users.id"))
    user: Mapped["User"] = relationship("User", back_populates="transactions")
    # END DELETE ME


class BalanceHistory(Base):
    __tablename__ = "balance_history"

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(sa.String(36), sa.ForeignKey("users.id"))
    balance: Mapped[Decimal]
    created_at: Mapped[datetime.datetime] = mapped_column(sa.DateTime, default=datetime.datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="balance_history")
