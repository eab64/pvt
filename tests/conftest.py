import typing

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import subprocess

# from app import ioc
from app.application import AppBuilder


@pytest.fixture(scope="session")
async def app_builder():
    subprocess.run(["alembic", "upgrade", "head"], check=True)
    
    builder = AppBuilder()
    await builder.init_async_resources()
    yield builder
    await builder.tear_down()


@pytest.fixture()
async def client(app_builder) -> typing.AsyncIterator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app_builder.app),  # type: ignore[arg-type]
        base_url="http://test",
    ) as client:
        yield client


@pytest.fixture(autouse=True)
async def clean_database(app_builder):
    async with app_builder._session_maker() as session:
        yield
        
        result = await session.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
        tables = [row[0] for row in result]
        
        await session.execute(text("SET session_replication_role = 'replica'"))
        
        for table in tables:
            if table != 'alembic_version':  # Не очищаем таблицу миграций
                await session.execute(text(f"TRUNCATE TABLE {table} CASCADE"))
        
        await session.execute(text("SET session_replication_role = 'origin'"))
        
        await session.commit()


#
# @pytest.fixture(autouse=True)
# async def _prepare_ioc_container() -> typing.AsyncIterator[None]:
#     engine = await ioc.IOCContainer.database_engine()
#     connection = await engine.connect()
#     transaction = await connection.begin()
#     await connection.begin_nested()
#     session = AsyncSession(connection, expire_on_commit=False, autoflush=False)
#     ioc.IOCContainer.session.override(session)
#
#     try:
#         yield
#     finally:
#         if connection.in_transaction():
#             await transaction.rollback()
#         await connection.close()
#
#         ioc.IOCContainer.reset_override()
#         await ioc.IOCContainer.tear_down()
