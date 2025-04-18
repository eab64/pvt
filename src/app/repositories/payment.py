import asyncio
from datetime import datetime
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession as AsyncSessionType,
)


import sqlalchemy as sa

from app import models, schemas
from app.exceptions import UserExistsError, PaymentError
from app.models import User, Transaction
from app.types import TransactionType


class PaymentRepository:

    def __init__(self, db_session_maker: async_sessionmaker[AsyncSessionType]):
        self.db_session_maker = db_session_maker

    async def create_user(self, data: schemas.UserCreate) -> User:
        ...
        # REMOVE ME
        try:
            async with self.db_session_maker.begin() as session:
                user = User(
                    id=data.id,
                    name=data.name,
                    balance=Decimal(0),
                )
                session.add(user)
        except IntegrityError:
            raise UserExistsError(f"User with id {data.id} already exists")
        return user
        # END REMOVE ME

    async def get_user_balance(self, user_id: str, ts: datetime | None = None) -> Decimal | None:
        # REMOVE ME
        async with self.db_session_maker() as session:
            if ts is None:
                query = sa.select(User.balance).where(User.id == user_id)
            else:
                query = sa.select(
                    sa.func.sum(Transaction.amount * sa.case(
                        (Transaction.type == TransactionType.WITHDRAW, sa.text('-1')),
                        else_=sa.text('1')
                    ))
                ).where(
                    sa.and_(
                        Transaction.user_id == user_id,
                        Transaction.created_at <= ts,
                    )
                )
            return (
                await session.execute(query)
            ).scalar()
        # END REMOVE ME

    async def add_transaction(self, data: schemas.TransactionAdd) -> Transaction:
        # REMOVE ME
        try:
            return await self._add_transaction(data)
        except IntegrityError:
            raise PaymentError(f"Transaction with uid {data.uid} already exists")

    async def _add_transaction(self, data: schemas.TransactionAdd) -> Transaction:
        async with self.db_session_maker.begin() as session:
            user = (
                await session.execute(
                    sa.select(User).with_for_update().where(User.id == data.user_id)
                )
            ).scalar()
            new_balance = (
                user.balance + data.amount if data.type == TransactionType.DEPOSIT else user.balance - data.amount
            )
            if new_balance < 0:
                raise PaymentError("Insufficient funds")

            await asyncio.sleep(1.0)  # simulate some latency

            transaction = Transaction(
                uid=data.uid,
                type=data.type,
                amount=data.amount,
                created_at=data.created_at,
                user_id=data.user_id,
            )
            session.add(transaction)
            await session.execute(
                sa.update(User)
                .where(User.id == data.user_id)
                .values(balance=new_balance)
            )
        return transaction
        # END REMOVE ME

    async def get_transaction(self, transaction_id: str) -> Transaction:
        async with self.db_session_maker() as session:
            transaction = (
                await session.execute(
                    sa.select(Transaction).where(Transaction.id == transaction_id)
                )
            ).scalar()
        return transaction
