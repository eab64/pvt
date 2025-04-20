import pytest
from httpx import AsyncClient
from decimal import Decimal
from datetime import datetime
import asyncio
import subprocess

from app.application import AppBuilder


@pytest.fixture
async def app_builder():
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    
    builder = AppBuilder()
    await builder.init_async_resources()
    yield builder
    await builder.tear_down()


@pytest.fixture
async def client(app_builder):
    async with AsyncClient(app=app_builder.app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_create_user(client):
    response = await client.post(
        "/api/user/",
        json={
            "id": "test-user-1-unique",
            "name": "Test User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-user-1-unique"
    assert data["name"] == "Test User"


@pytest.mark.asyncio
async def test_create_duplicate_user(client):
    await client.post(
        "/api/user/",
        json={
            "id": "test-user-2-unique",
            "name": "Test User"
        }
    )
    
    response = await client.post(
        "/api/user/",
        json={
            "id": "test-user-2-unique",
            "name": "Test User"
        }
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_create_deposit_transaction(client):
    await client.post(
        "/api/user/",
        json={
            "id": "test-user-3-unique",
            "name": "Test User"
        }
    )
    
    response = await client.put(
        "/api/transaction/",
        json={
            "uid": "tx-1-unique",
            "user_id": "test-user-3-unique",
            "amount": "1000.0",
            "created_at": "2023-01-01T01:00:00",
            "type": "DEPOSIT"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["uid"] == "tx-1-unique"
    assert data["amount"] == "1000.0"
    assert data["type"] == "DEPOSIT"


@pytest.mark.asyncio
async def test_create_withdraw_transaction(client):
    await client.post(
        "/api/user/",
        json={
            "id": "test-user-4-unique",
            "name": "Test User"
        }
    )
    
    await client.put(
        "/api/transaction/",
        json={
            "uid": "tx-2-unique",
            "user_id": "test-user-4-unique",
            "amount": "1000.0",
            "created_at": "2023-01-01T01:00:00",
            "type": "DEPOSIT"
        }
    )
    
    response = await client.put(
        "/api/transaction/",
        json={
            "uid": "tx-3-unique",
            "user_id": "test-user-4-unique",
            "amount": "500.0",
            "created_at": "2023-01-02T01:00:00",
            "type": "WITHDRAW"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["uid"] == "tx-3-unique"
    assert data["amount"] == "500.0"
    assert data["type"] == "WITHDRAW"


@pytest.mark.asyncio
async def test_insufficient_funds(client):
    await client.post(
        "/api/user/",
        json={
            "id": "test-user-5-unique",
            "name": "Test User"
        }
    )
    
    response = await client.put(
        "/api/transaction/",
        json={
            "uid": "tx-4-unique",
            "user_id": "test-user-5-unique",
            "amount": "1000.0",
            "created_at": "2023-01-01T01:00:00",
            "type": "WITHDRAW"
        }
    )
    assert response.status_code == 409
    assert "Insufficient funds" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_balance(client):
    await client.post(
        "/api/user/",
        json={
            "id": "test-user-6-unique",
            "name": "Test User"
        }
    )
    
    await client.put(
        "/api/transaction/",
        json={
            "uid": "tx-5-unique",
            "user_id": "test-user-6-unique",
            "amount": "1000.0",
            "created_at": "2023-01-01T01:00:00",
            "type": "DEPOSIT"
        }
    )
    
    response = await client.get(f"/api/user/test-user-6-unique/balance/")
    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == "1000.0"


@pytest.mark.asyncio
async def test_get_balance_at_date(client):
    await client.post(
        "/api/user/",
        json={
            "id": "test-user-7-unique",
            "name": "Test User"
        }
    )
    
    await client.put(
        "/api/transaction/",
        json={
            "uid": "tx-6-unique",
            "user_id": "test-user-7-unique",
            "amount": "1000.0",
            "created_at": "2023-01-01T01:00:00",
            "type": "DEPOSIT"
        }
    )
    
    await client.put(
        "/api/transaction/",
        json={
            "uid": "tx-7-unique",
            "user_id": "test-user-7-unique",
            "amount": "500.0",
            "created_at": "2023-01-02T01:00:00",
            "type": "WITHDRAW"
        }
    )
    
    response = await client.get(
        f"/api/user/test-user-7-unique/balance/?ts=2023-01-01T12:00:00"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["balance"] == "1000.0"


@pytest.mark.asyncio
async def test_get_transaction(client):
    await client.post(
        "/api/user/",
        json={
            "id": "test-user-8-unique",
            "name": "Test User"
        }
    )
    
    await client.put(
        "/api/transaction/",
        json={
            "uid": "tx-8-unique",
            "user_id": "test-user-8-unique",
            "amount": "1000.0",
            "created_at": "2023-01-01T01:00:00",
            "type": "DEPOSIT"
        }
    )
    
    response = await client.post(f"/api/transaction/tx-8-unique")
    assert response.status_code == 200
    data = response.json()
    assert data["uid"] == "tx-8-unique"
    assert data["amount"] == "1000.0"
    assert data["type"] == "DEPOSIT" 