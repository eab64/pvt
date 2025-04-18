from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncSession as AsyncSessionType,
)


from app.settings import Settings
from app.repositories import PaymentRepository


def get_settings() -> Settings:
    raise NotImplementedError


def get_db() -> async_sessionmaker[AsyncSessionType]:
    raise NotImplementedError


def get_payment_repo(
    db: async_sessionmaker[AsyncSessionType] = Depends(get_db),
) -> PaymentRepository:
    return PaymentRepository(
        db_session_maker=db,
    )
