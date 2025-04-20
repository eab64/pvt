from datetime import datetime
import typing

import fastapi
from starlette import status

from app import schemas
from app.exceptions import PaymentError, UserExistsError
from app.repositories import PaymentRepository
from app.api.base import get_payment_repo


ROUTER: typing.Final = fastapi.APIRouter()

@ROUTER.get("/")
async def root():
    return {"status": "OK", "message": "API работает!"}

@ROUTER.post("/user/")
async def create_user(
    data: schemas.UserCreate,
    payment_repo: PaymentRepository = fastapi.Depends(get_payment_repo),
) -> schemas.User:
    try:
        user = await payment_repo.create_user(data)
    except UserExistsError as e:
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    return typing.cast(schemas.User, user)


@ROUTER.get("/user/{user_id}/balance/")
async def get_user_balance(
    user_id: str,
    ts: datetime | None = None,
    payment_repo: PaymentRepository = fastapi.Depends(get_payment_repo),
) -> schemas.UserBalance:
    balance = await payment_repo.get_user_balance(user_id, ts=ts)
    if balance is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return typing.cast(schemas.UserBalance, {"balance": balance})


@ROUTER.put("/transaction/")
async def add_transaction(
    data: schemas.TransactionAdd,
    payment_repo: PaymentRepository = fastapi.Depends(get_payment_repo),
) -> schemas.Transaction:
    try:
        transaction = await payment_repo.add_transaction(data)
    except PaymentError as e:
        raise fastapi.HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    return typing.cast(schemas.Transaction, transaction)


@ROUTER.post("/transaction/{transaction_id}")
async def get_transaction(
    transaction_id: str,
    payment_repo: PaymentRepository = fastapi.Depends(get_payment_repo),
) -> schemas.Transaction:
    transaction = await payment_repo.get_transaction(transaction_id)
    if transaction is None:
        raise fastapi.HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
    return typing.cast(schemas.Transaction, transaction)

